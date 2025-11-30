/**
 * @file gsm_diom_ii_db.cpp
 *
 * @author Will Bolduc <wbolduc@cs.utexas.edu>
 * @author Michael Goppert <goppert@cs.utexas.edu>
 */

// This is f*cky.
//
// Need to include implementation, but can't do it in header file unilateral
// because of ODR. But, header only included once!
//
// Add it here and pray for the best.
#define KVSTORE_GSM_DIOM_II_IMPL
#include "gsm_diom_ii_db.h"

#include <cassert>

namespace ycsbc {

gsm_diom_ii_db::gsm_diom_ii_db(const utils::Properties &props) {}

DB::Status gsm_diom_ii_db::Read(const std::string &table,
                                const std::string &key,
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

DB::Status gsm_diom_ii_db::Scan(const std::string &table,
                                const std::string &key, int len,
                                const std::vector<std::string> *fields,
                                std::vector<std::vector<Field>> &result) {
    // Not implementable.
    return kOK;
}

DB::Status gsm_diom_ii_db::Update(const std::string &table,
                                  const std::string &key,
                                  std::vector<Field> &values) {
    _map.set(key, values[0].value);
    return kOK;
}

DB::Status gsm_diom_ii_db::Insert(const std::string &table,
                                  const std::string &key,
                                  std::vector<Field> &values) {
    _map.set(key, values[0].value);
    return kOK;
}

DB::Status gsm_diom_ii_db::Delete(const std::string &table,
                                  const std::string &key) {
    _map.remove(key);
    return kOK;
}

kvstore::sync_map_diom_ii gsm_diom_ii_db::_map;

} // namespace ycsbc
