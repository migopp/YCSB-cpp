/**
 * @file openjdk_concurrent_hash_map.cpp
 *
 * @author Michael Goppert <goppert@cs.utexas.edu>
 * @author Will Bolduc <wbolduc@cs.utexas.edu>
 */

#include "openjdk_concurrent_hash_map.h"
#include "core/db_factory.h"

#define KVSTORE_OJDKCHM_IMPL
#include <kvstore/openjdk_concurrent_hash_map.h>

namespace ycsbc {

DB *concurrent_hash_map::init() { return new concurrent_hash_map(); }

concurrent_hash_map::concurrent_hash_map(const utils::Properties &props) {}

DB::Status concurrent_hash_map::Read(const std::string &table,
                                     const std::string &key,
                                     const std::vector<std::string> *fields,
                                     std::vector<Field> &result) {
    return kOK;
}

DB::Status concurrent_hash_map::Scan(const std::string &table,
                                     const std::string &key, int len,
                                     const std::vector<std::string> *fields,
                                     std::vector<std::vector<Field>> &result) {
    return kOK;
}

DB::Status concurrent_hash_map::Update(const std::string &table,
                                       const std::string &key,
                                       std::vector<Field> &values) {
    return kOK;
}

DB::Status concurrent_hash_map::Insert(const std::string &table,
                                       const std::string &key,
                                       std::vector<Field> &values) {
    return kOK;
}

DB::Status concurrent_hash_map::Delete(const std::string &table,
                                       const std::string &key) {
    return kOK;
}

bool concurrent_hash_map::_registered = DBFactory::RegisterDB(
    "openjdk_concurrent_hash_map", concurrent_hash_map::init);
} // namespace ycsbc
