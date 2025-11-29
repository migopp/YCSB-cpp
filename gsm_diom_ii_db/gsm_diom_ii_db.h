/**
 * @file gsm_diom_ii_db.h
 *
 * @author Will Bolduc <wbolduc@cs.utexas.edu>
 * @author Michael Goppert <goppert@cs.utexas.edu>
 */

#pragma once

#include "core/db.h"
#include <kvstore/go_sync_map_diom_ii.h>

namespace ycsbc {

class gsm_diom_ii_db : public DB {
  public:
    gsm_diom_ii_db() = default;

    gsm_diom_ii_db(const utils::Properties &props);

    virtual ~gsm_diom_ii_db() = default;

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
    static kvstore::sync_map_diom_ii _map;
};

} // namespace ycsbc
