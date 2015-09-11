# Quick Start #

You can get the source code of Express-Persist from
http://express-me.googlecode.com/svn/trunk/ExpressPersist. Run ant to build the
project and get the `express-persist.jar` in `dist` directory. Or you can download
from http://code.google.com/p/express-me/downloads/list?q=Express-Persist.

# Overview #

Support we have one database with one table named "User", with fields:

  * id varchar(32) primary key,
  * password varchar(32) not null,
  * name varchar(50) not null.

Here is a sample of UserDao to demonstrate how to define your DAO interface and
get ready to use:

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

OK, we have DAO interface, but we **DO NOT** write the implemented class, so we
can use the `UserDao` now without any JDBC code!

Now we can use this interface now:

```
UserDao dao = createUserDao(); // discuss later
User u1 = new User("id-12345", "password", "Michael");
dao.createUser(u1);

User u2 = queryUser("abc1234");
u2.setName("Michael Liao");
u2.setPassword("abcdefg");
dao.updateUser(u2);
```

It is simple. All you need to do is carefully defining your DAO interface, and
let Express-Persist do all JDBC jobs for you.

If you want to know more details about Express-Persist, see [Developer's Guide](ExpressPersistDeveloper.md).