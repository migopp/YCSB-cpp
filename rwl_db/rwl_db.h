/**
 * @file rwl_db.h
 *
 * @author Michael Goppert <goppert@cs.utexas.edu>
 * @author Will Bolduc <wbolduc@cs.utexas.edu>
 */

#pragma once

#include "core/db.h"
#include <kvstore/rwlock_hash_map.h>

namespace ycsbc {

class rwl_db : public DB {
  public:
    rwl_db() = default;

    rwl_db(const utils::Properties &props);

    virtual ~rwl_db() = default;

    DB::Status Read(const std::string &table, const std::string &key,
                    const std::vector<std::string> *fields,
                    std::vector<Field> &result);

    DB::Status Scan(const std::string &table, const std::string &key, int len,
                    const std::vector<std::string> *fields,
                    std::vector<std::vector<Field>> &result);

    DB::Status Update(const std::string &table, const std::string &key,
                      std::vector<Field> &values);

    DB::Status Insert(const std::string &table, const std::string &key,
                      std::vector<Field> &values);

    DB::Status Delete(const std::string &table, const std::string &key);

  private:
    static kvstore::rwlock_hash_map _map;
};

} // namespace ycsbc
