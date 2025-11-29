#pragma once
#include "core/db.h"
#include "gsm_db/gsm_common.h"
#include <atomic>
#include <iostream>
#include <memory>
#include <string>

extern std::shared_ptr<std::string> expunged;

class gsm_diom_ii_db : public ycsbc::DB {
  public:
    gsm_diom_ii_db();
    ~gsm_diom_ii_db() override = default;
    void Init();
    void Cleanup();

    DB::Status Read(const std::string &table, const std::string &key,
                    const std::vector<std::string> *fields,
                    std::vector<Field> &result);

    DB::Status Insert(const std::string &table, const std::string &key,
                      std::vector<Field> &values) override;

    DB::Status Update(const std::string &table, const std::string &key,
                      std::vector<Field> &values) override;

    DB::Status Delete(const std::string &table,
                      const std::string &key) override;

    // Fine mr compiler. You may do this.
    Status Scan(const std::string &table, const std::string &key, int len,
                const std::vector<std::string> *fields,
                std::vector<std::vector<Field>> &result) override;

  private:
    std::atomic<std::shared_ptr<readOnlyMapHolder>> readOnlyMapAtomicPointer;
    std::shared_ptr<dataMap> dirtyMap;
    std::atomic<long unsigned int> missesForCurrentDirtyMap;
    std::mutex dirtyLock;

    std::shared_ptr<readOnlyMapHolder> getReadOnlyMap() {
        return std::atomic_load(&readOnlyMapAtomicPointer);
    }

    readOnlyMapValue getValueFromReadOnlyMap(const std::string &key) {
        readOnlyMapValue output;
        std::shared_ptr<readOnlyMapHolder> readOnlyMapHolderPointer =
            getReadOnlyMap();
        std::shared_ptr<dataMap> readOnlyMap =
            readOnlyMapHolderPointer->readOnlyMap;
        // check if the key is even in there lol
        // safe to do since we should never be adding or removing entries from
        // this map
        if (readOnlyMap->find(key) != readOnlyMap->end()) {
            // Yay, we can just return the value
            std::shared_ptr<mapEntry> foundEntry = readOnlyMap->at(key);

            std::shared_ptr<std::string> entryDataPointer =
                std::atomic_load(&foundEntry->dataPointer);
            output.value = entryDataPointer;
            output.hasBeenAmmended = readOnlyMapHolderPointer->hasBeenAmmended;
            return output;
        } else {
            output.value = nullptr;
            output.hasBeenAmmended = readOnlyMapHolderPointer->hasBeenAmmended;
            return output;
        }
    }

    readOnlyMapEntryReturn getEntryFromReadOnlyMap(const std::string &key) {
        readOnlyMapEntryReturn output;
        std::shared_ptr<readOnlyMapHolder> readOnlyMapHolderPointer =
            getReadOnlyMap();
        std::shared_ptr<dataMap> readOnlyMap =
            readOnlyMapHolderPointer->readOnlyMap;
        // check if the key is even in there lol
        // safe to do since we should never be adding or removing entries from
        // this map
        if (readOnlyMap->find(key) != readOnlyMap->end()) {
            // Yay, we can just return the value
            std::shared_ptr<mapEntry> foundEntry = readOnlyMap->at(key);

            output.entry = foundEntry;
            output.hasBeenAmmended = readOnlyMapHolderPointer->hasBeenAmmended;
            return output;
        } else {
            output.entry = nullptr;
            output.hasBeenAmmended = readOnlyMapHolderPointer->hasBeenAmmended;
            return output;
        }
    }

    void increaseMisses() {
        long unsigned int currentMisses = missesForCurrentDirtyMap.fetch_add(1);
        // std::cout << "Uh oh! Too many misses, better expand da lol no.
        // Current size = " << dirtyMap->size() << " currentMisses = " <<
        // currentMisses << "\n";
        if (currentMisses >= dirtyMap->size()) {
            // std::cout << "Uh oh! Too many misses, better expand da map. "
            //              "Current size = "
            //           << dirtyMap->size()
            //           << " currentMisses = " << currentMisses << "\n";
            // make a new readOnlyMapHolder
            std::shared_ptr<readOnlyMapHolder> newHolder =
                std::make_shared<readOnlyMapHolder>();
            newHolder->readOnlyMap = dirtyMap;
            newHolder->hasBeenAmmended = false;
            missesForCurrentDirtyMap.store(0);
            dirtyMap = nullptr;
            std::atomic_store(&readOnlyMapAtomicPointer, newHolder);
        }
    }

    void makeNewDirtyMap() {
        if (dirtyMap != nullptr) {
            return;
        }

        std::shared_ptr<readOnlyMapHolder> readOnlyMapHolderPointer =
            getReadOnlyMap();
        std::shared_ptr<dataMap> readOnlyMap =
            readOnlyMapHolderPointer->readOnlyMap;

        dirtyMap = std::make_shared<dataMap>();

        // Iterate over all entries in the read only map. If the current value
        // is not nil, copy it over. If it is, mark it as expunged and dont copy
        // it over
        for (const auto &[key, entry] : *readOnlyMap) {
            std::shared_ptr<std::string> currentValue =
                entry->dataPointer.load();

            bool entryIsExpunged = (currentValue == nullptr);
            while (entryIsExpunged) {
                std::shared_ptr<std::string> expected = nullptr;
                if (entry->dataPointer.compare_exchange_strong(expected,
                                                               expunged)) {
                    entryIsExpunged = true;
                    break;
                }
                currentValue = entry->dataPointer.load();

                entryIsExpunged = (currentValue == nullptr);
            }
            if (!entryIsExpunged) {
                (*dirtyMap)[key] = entry;
            }
        }
    }
};
