/**
 * @file rwl_db.cpp
 *
 * @author Michael Goppert <goppert@cs.utexas.edu>
 * @author Will Bolduc <wbolduc@cs.utexas.edu>
 */

// This is f*cky.
//
// Need to include implementation, but can't do it in header file unilateral
// because of ODR. But, header only included once!
//
// Add it here and pray for the best.
#define KVSTORE_RWLHM_IMPL
#include "rwl_db.h"

#include "core/db_factory.h"
#include <cassert>

namespace ycsbc {

rwl_db::rwl_db(const utils::Properties &props) {}

DB::Status rwl_db::Read(const std::string &table, const std::string &key,
                        const std::vector<std::string> *fields,
                        std::vector<Field> &result) {
    auto res = _map.get(key);
    if (res.has_value()) {
        result.push_back({key, res.value()});
        return kOK;
    } else {
        return kNotFound;
    }
}

DB::Status rwl_db::Scan(const std::string &table, const std::string &key,
                        int len, const std::vector<std::string> *fields,
                        std::vector<std::vector<Field>> &result) {
    // Not implementable.
    return kOK;
}

DB::Status rwl_db::Update(const std::string &table, const std::string &key,
                          std::vector<Field> &values) {
    assert(values.size() == 1); // Only expected to update one value.
    auto res = _map.set(key, values[0].value);
    assert(res.has_value()); // Should already be present in the map.
    return kOK;
}

DB::Status rwl_db::Insert(const std::string &table, const std::string &key,
                          std::vector<Field> &values) {
    assert(values.size() == 1); // Only expected to insert one value.
    auto res = _map.set(key, values[0].value);
    assert(!res.has_value()); // Should not already be present in the map.
    return kOK;
}

DB::Status rwl_db::Delete(const std::string &table, const std::string &key) {
    auto res = _map.remove(key);
    assert(res.has_value()); // Should be in the map already.
    return kOK;
}

kvstore::rwlock_hash_map rwl_db::_map;

} // namespace ycsbc
