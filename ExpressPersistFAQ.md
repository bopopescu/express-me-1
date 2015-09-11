# FAQ #

Here are some common issues you may encountered.

## Supported SQL Types ##

Not all the SQL types are supported by Express-Persist. The supported SQL types
and its corresponding Java types are:

| **SQL Type** | **Java Type** |
|:-------------|:--------------|
| bit, boolean | boolean       |
| tinyint, smallint | short         |
| integer      | int           |
| bigint       | long          |
| real         | float         |
| float, double | double        |
| varchar      | java.lang.String |
| date, time, timestamp | java.util.Date |
| binary, varbinary, longvarbinary | byte[.md](.md) |
| decimal, numeric | java.math.BigDecimal |

## Supported Dialects ##

The dialect is used to do database-specific function. Express-Persist supports
HSQLDB, MySQL and Oracle dialects which are placed under package
`org.expressme.persist.dialect`.

You can write your own dialect to support more database, by implementing
`org.expressme.persist.dialect.Dialect` interface.

## Problems in RMI ##

Express-Persist only support local JDBC transaction, and it binds transaction
into `ThreadLocal`, so transaction is only available to current thread, and
cannot across any remote procedure calls such as Java RMI.

## Can I Use SQL Functions ##

Yes. You can get the value by appropriate RowMapper:

```
@Unique
@MappedBy(IntegerRowMapper.class)
@Query("select count(*) from User")
int getUserCount();
```