#pragma once

#include <atomic>
#include <memory>
#include <unordered_map>

struct mapEntry {
    std::atomic<std::shared_ptr<std::string>> dataPointer;
};

using dataMap = std::unordered_map<std::string, std::shared_ptr<mapEntry>>;

struct readOnlyMapHolder {
    std::shared_ptr<dataMap> readOnlyMap;
    bool hasBeenAmmended = false;
};

// struct that just exists to give us an easy way of returning two values. God I
// miss Go.
struct readOnlyMapValue {
    std::shared_ptr<std::string> value;
    bool hasBeenAmmended;
};

struct readOnlyMapEntryReturn {
    std::shared_ptr<mapEntry> entry;
    bool hasBeenAmmended;
};
