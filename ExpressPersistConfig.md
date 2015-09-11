# Configuration #

Express-Persist is a lightweight framework that encapsulates JDBC APIs, so it
requires one and only one DataSource but it does not support JTA.

Assume that we have our `User` class which is a simple JavaBean:

```
public class User {
    private String id;
    private String password;
    private String name;
    // getters and setters here:
    // TODO: ...
}
```

Now let's begin to write `UserDao` interface for this `User` class.

## Lookup DataSource ##

The first step is lookup DataSource from somewhere. It is usually got from JNDI
when application is running on JavaEE server. You can still create a DataSource
for test purpose by using DriverManagerDataSource provided by Express-Persist:

```
DataSource dataSource = new DriverManagerDataSource(
        "org.hsqldb.jdbcDriver", // driver class
        "jdbc:hsqldb:mem:test", // url
        "sa", // username
        "" // password
);
```

We choose [HSQLDB](http://hsqldb.org/) (a pure Java database that can run in memory)
as database for test.

## Define DAO Interface ##

Now we can define `UserDao` interface:

```
public interface UserDao {
    @Unique
    @MappedBy(UserRowMapper.class)
    @Query("select * from User u where u.id=:id")
    User queryUser(@Param("id") String id);

    @MappedBy(UserRowMapper.class)
    @Query("select * from User u order by u.name desc")
    List<User> queryUsers(@FirstResult int first, @MaxResults int max);

    @Update("insert into User(id, password, name) values(:u.id, :u.password, :u.name)")
    void createUser(@Param("u") User user);

    @Update("update User set password=:u.password, name=:u.name where id=:u.id")
    void updateUser(@Param("u") User user);
}
```

## Use DAO ##

We can use `UserDao` with little code:

```
// create transaction manager:
TransactionManager txManager = new TransactionManager(dataSource);

// create DAO factory with HSQLDB support:
DAOFactory daoFactory = new DAOFactory(new HSQLDBDialect());

// create UserDao:
UserDao userDao = daoFactory.createDao(UserDao.class, txManager);

// use UserDao:
Transaction tx = txManager.beginTransaction();

User u1 = new User("id-12345", "password", "Michael");
dao.createUser(u1);

User u2 = queryUser("abc1234");
u2.setName("Michael Liao");
u2.setPassword("abcdefg");
dao.updateUser(u2);

tx.commit();
```

There is no JDBC code. We just define the interface with some annotation.
To continue Express-Persist, please see how to use [Query](ExpressPersistQuery.md)
and [Update](ExpressPersistUpdate.md).

The transaction code usually is put in `Filter` or `Interceptor` in web
applications, so it only requires write once.