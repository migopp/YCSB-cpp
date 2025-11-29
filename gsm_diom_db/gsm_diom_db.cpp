#include "gsm_diom_db.h"

using namespace ycsbc;

gsm_diom_db::gsm_diom_db() {}

void gsm_diom_db::Init() {
    std::lock_guard<std::mutex> lock(dirtyLock);

    // Only initialize once
    if (readOnlyMapAtomicPointer.load() == nullptr) {
        std::shared_ptr<dataMap> newReadOnlyMap = std::make_shared<dataMap>();
        std::shared_ptr<readOnlyMapHolder> newHolder =
            std::make_shared<readOnlyMapHolder>();
        newHolder->readOnlyMap = newReadOnlyMap;
        newHolder->hasBeenAmmended = false;
        std::atomic_store(&readOnlyMapAtomicPointer, newHolder);
    }
}

void gsm_diom_db::Cleanup() {
    // Nothing needed
}

extern bool makeNullptrIfExpunged(std::shared_ptr<mapEntry> entry);

// return false if it was expunged
extern bool
swapEntryValueIfEntryIsNotExpunged(std::shared_ptr<mapEntry> entry,
                                   std::shared_ptr<std::string> newValue);

extern void deleteEntry(std::shared_ptr<mapEntry> entry);

DB::Status gsm_diom_db::Read(const std::string &, const std::string &key,
                             const std::vector<std::string> *,
                             std::vector<Field> &result) {

    // Step one: please oh please can we just find it in the read only map
    // pretty please
    readOnlyMapValue valueFoundFromReadOnly = getValueFromReadOnlyMap(key);

    if (valueFoundFromReadOnly.value != nullptr) {
        result.push_back({key, *(valueFoundFromReadOnly.value)});
        return kOK;
    }
    // std::cout << "whats up gamer we out here reading more than we should have
    // \n";

    // Ugh. Maybe it hasn't been ammended?

    if (valueFoundFromReadOnly.hasBeenAmmended == false) {
        return kNotFound;
    }

    // uuuuuuuuuugh. Check the dirty map.
    // need to take the lock
    std::lock_guard<std::mutex> lock(dirtyLock);
    // std::cout << "We had to take the lock. this is a tragedy \n";
    // Double check rq if the read map got this guy
    valueFoundFromReadOnly = getValueFromReadOnlyMap(key);

    if (valueFoundFromReadOnly.value != nullptr) {
        result.push_back({key, *(valueFoundFromReadOnly.value)});
        // std::cout << "whats up gamer wtf \n";
        return kOK;
    }
    if (valueFoundFromReadOnly.hasBeenAmmended == false) {
        // std::cout << "whats up wth \n";
        return kNotFound;
    }
    // std::cout << "whats up gamer we out here reading way more than we should
    // have \n";

    // FINE! READ THE DIRTY MAP. see if I care
    std::shared_ptr<dataMap> currentDirtyMap = dirtyMap;

    if (currentDirtyMap->find(key) != currentDirtyMap->end()) {
        std::shared_ptr<mapEntry> dirtyEntry = currentDirtyMap->at(key);
        std::shared_ptr<std::string> entryDataPointer =
            std::atomic_load(&(dirtyEntry->dataPointer));
        result.push_back({key, *(entryDataPointer)});
        increaseMisses();
        return kOK;
    } else {
        // still report a miss, since we had to look in the dirty map
        // TODO - it feels like it would be better to not do this
        // std::cout << "so this should NEVER happen \n";
        // increaseMisses();
        return kNotFound;
    }
}

DB::Status gsm_diom_db::Insert(const std::string &, const std::string &key,
                               std::vector<Field> &values) {

    // Aight lets store some stuff woo
    std::string userValue = values[0].value;
    std::shared_ptr<std::string> valuePtr =
        std::make_shared<std::string>(userValue);
    // std::cout << "whats up gamer we out here inserting \n";

    // first up: check if its in the read map
    readOnlyMapEntryReturn entryFoundFromReadOnly =
        getEntryFromReadOnlyMap(key);
    if (entryFoundFromReadOnly.entry != nullptr) {
        // std::cout << "whats up gamer entry " << key << " we out here already
        // having inserted somehow what da hellie \n\n\n\n"; if so, try to swap
        // in the value if this works, we gucci if it does not (the value was
        // expunged) then we gotta go put in some work in the dirty map
        bool wasExpunged = swapEntryValueIfEntryIsNotExpunged(
            entryFoundFromReadOnly.entry, valuePtr);
        if (!wasExpunged) {
            // we are done!
            return kOK;
        }
    }
    // std::cout << "whats up gamer entry " << key << " we out here not already
    // having inserted somehow what da hellie \n";

    // Dirty map time woo: take that lock bestie
    std::lock_guard<std::mutex> lock(dirtyLock);

    entryFoundFromReadOnly = getEntryFromReadOnlyMap(key);
    // Get the read map again. If it has an entry:
    if (entryFoundFromReadOnly.entry != nullptr) {
        bool wasExpunged = makeNullptrIfExpunged(entryFoundFromReadOnly.entry);
        // if that entry's current value is expunged, make it nullptr and put
        // this entry into the dirty map as well. now, any change to the entry
        // contents will affect both the dirty map and the readable map (I
        // think), but atomically so we chilling
        if (wasExpunged) {
            (*dirtyMap)[key] = entryFoundFromReadOnly.entry;
        }

        // Then, unconidtionally put the new value into that entry atomically
        entryFoundFromReadOnly.entry->dataPointer.exchange(valuePtr);

        // we are done!
        return kOK;
    }

    // if it does not have an entry:
    if (entryFoundFromReadOnly.hasBeenAmmended) {
        // We already have a dirty map. if it has an entry for this, we can just
        // swap in the value
        if (dirtyMap->find(key) != dirtyMap->end()) {
            std::shared_ptr<mapEntry> dirtyEntry = dirtyMap->at(key);
            dirtyEntry->dataPointer.exchange(valuePtr);
            // we are done!
            return kOK;
        }
    }
    // If either is false:
    // check if dirty exists
    if (!entryFoundFromReadOnly.hasBeenAmmended) {
        // nope! ok, we need to go ahead and make a new one.
        std::cout << "This should literally never happen \n";
        makeNewDirtyMap();
        // Mark ammended
        std::shared_ptr<readOnlyMapHolder> newHolder =
            std::make_shared<readOnlyMapHolder>();
        newHolder->readOnlyMap = getReadOnlyMap()->readOnlyMap;
        newHolder->hasBeenAmmended = true;
        std::atomic_store(&readOnlyMapAtomicPointer, newHolder);
    }
    // Now, either way, we can make a nice pretty new entry.
    std::shared_ptr<mapEntry> newEntry = std::make_shared<mapEntry>();
    newEntry->dataPointer.store(valuePtr);
    (*dirtyMap)[key] = newEntry;
    return kOK;
}

DB::Status gsm_diom_db::Update(const std::string &, const std::string &key,
                               std::vector<Field> &values) {
    return Insert("", key, values); // same
}

// The cool part of this: we don't actually remove the entry till
// we make another dirty map and it gets promoted
// to avoid having to do nasty locking or removing entries from data structures
DB::Status gsm_diom_db::Delete(const std::string &, const std::string &key) {
    readOnlyMapEntryReturn entryFoundFromReadOnly =
        getEntryFromReadOnlyMap(key);
    if (entryFoundFromReadOnly.entry != nullptr) {
        // Just delete this entry!'
        deleteEntry(entryFoundFromReadOnly.entry);
        return kOK;
    }

    if (entryFoundFromReadOnly.hasBeenAmmended == false) {
        // no point in checking the dirty map, it hasn't been ammended.
        // it might have been ammended since we started, but that guarantees
        // that the delete raced with the write, so we can just choose not to
        // delete
        return kOK;
    }

    // Ok, grab the lock and try again
    std::lock_guard<std::mutex> lock(dirtyLock);

    entryFoundFromReadOnly = getEntryFromReadOnlyMap(key);
    if (entryFoundFromReadOnly.entry != nullptr) {
        // Just delete this entry!'
        deleteEntry(entryFoundFromReadOnly.entry);
        return kOK;
    }

    if (entryFoundFromReadOnly.hasBeenAmmended == false) {
        // no point in checking the dirty map, it hasn't been ammended.
        return kOK;
    }

    // Ok, it has been ammended and we didn't find it, so check the dirty map
    std::shared_ptr<dataMap> currentDirtyMap = dirtyMap;

    if (currentDirtyMap->find(key) != currentDirtyMap->end()) {
        std::shared_ptr<mapEntry> dirtyEntry = currentDirtyMap->at(key);
        deleteEntry(dirtyEntry);

        increaseMisses();
        return kOK;
    } else {
        // still report a miss, since we had to look in the dirty map
        // TODO - it feels like it would be better to not do this
        increaseMisses();
        return kOK;
    }
}

// Stupid dumb useless function that the compiler demands
DB::Status gsm_diom_db::Scan(const std::string &table, const std::string &key,
                             int len, const std::vector<std::string> *fields,
                             std::vector<std::vector<Field>> &result) {

    return kOK;
}
