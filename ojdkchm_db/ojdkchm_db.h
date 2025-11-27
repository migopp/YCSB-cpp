/**
 * @file ojdkchm_db.h
 *
 * @author Michael Goppert <goppert@cs.utexas.edu>
 * @author Will Bolduc <wbolduc@cs.utexas.edu>
 */

#pragma once

#include "core/db.h"
#include <kvstore/openjdk_concurrent_hash_map.h>

namespace ycsbc {

class ojdkchm_db : public DB {
  public:
    ojdkchm_db() = default;

    ojdkchm_db(const utils::Properties &props);

    virtual ~ojdkchm_db() = default;

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
    static kvstore::concurrent_hash_map _map;
};

} // namespace ycsbc
