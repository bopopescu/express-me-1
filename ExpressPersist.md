# Introduction #

Express-Persist is a sub-project of ExpressMe for persistence to reduce the
complexity of JDBC. It is a persistence framework that only require DAO
interface but without any JDBC code.

# Features #

Features of Express-Persist:

  * Java 5 annotation-based configuration of DAO interface.
  * Dynamically create DAO instance from your DAO interface without JDBC code at runtime.
  * Abstraction of Transaction layer, only support local transaction.

The design goal of Express-Persist is:

  * Speed! Get as fast as JDBC code.
  * Lightweight! Only use JavaBean, no CGLIB, no any other 3rd-part library except commons-logging.
  * Less code, but more check!

# Benefit #

You can use Express-Persist:

  * Avoid write DAO classes;
  * Avoid any JDBC code with `try ... catch (SQLException e) ... finally ...`;
  * Do not worry about acquire and release JDBC resources (Connection, ResultSet, etc.);
  * Get full benefit of JDBC: speed, vender-specific SQL, etc.;
  * Unique result check, SQL parameters check, limited-query support;
  * ResultSet to Object mapping;
  * Easy to add more database support.