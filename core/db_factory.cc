//
//  basic_db.cc
//  YCSB-cpp
//
//  Copyright (c) 2020 Youngjae Lee <ls4154.lee@gmail.com>.
//  Copyright (c) 2014 Jinglei Ren <jinglei@ren.systems>.
//

#include "db_factory.h"
#include "basic_db.h"
#include "db_wrapper.h"

#include "gsm_db/gsm_db.h"
#include "ojdkchm_db/ojdkchm_db.h"
#include "rwl_db/rwl_db.h"

namespace ycsbc {

namespace {

bool ojdkchm_db_registered = DBFactory::RegisterDB(
    "ojdkchm_db", []() -> DB * { return new ojdkchm_db(); });

bool rwl_db_registered =
    DBFactory::RegisterDB("rwl_db", []() -> DB * { return new rwl_db(); });

bool gsm_db_registered =
    DBFactory::RegisterDB("gsm_db", []() -> DB * { return new gsm_db(); });

} // namespace

std::map<std::string, DBFactory::DBCreator> &DBFactory::Registry() {
  static std::map<std::string, DBCreator> registry;
  return registry;
}

bool DBFactory::RegisterDB(std::string db_name, DBCreator db_creator) {
  Registry()[db_name] = db_creator;
  return true;
}

DB *DBFactory::CreateDB(utils::Properties *props, Measurements *measurements) {
  std::string db_name = props->GetProperty("dbname", "basic");
  DB *db = nullptr;
  std::map<std::string, DBCreator> &registry = Registry();
  if (registry.find(db_name) != registry.end()) {
    DB *new_db = (*registry[db_name])();
    new_db->SetProps(props);
    db = new DBWrapper(new_db, measurements);
  }
  return db;
}

} // namespace ycsbc
