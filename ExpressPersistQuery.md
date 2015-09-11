# Using Query #

A Query method is defined with annotation `@Query`, containing Your SQL statement.
The arguments of method will be pass as SQL parameters. Because the sequence of
method's arguments may differ from the sequence of SQL parameters, the SQL
parameters must be defined as 'named' parameters rather than '?'.

For example, if we want to query a User object by its id, use following definition:

```
@Unique
@MappedBy(UserRowMapper.class)
@Query("select * from User u where u.id=:id")
User queryUser(@Param("id") String id);
```

The SQL parameter is defined as `:id`, which is mapping to argument with annotion
`@Param("id")`. Express-Persist will finally generate the prepared SQL statement
like `select * from User u where u.id=?` and pass argument `id` as SQL parameter.

Next, Express-Persist needs to know how to map a row of ResultSet to a Java object,
so `@MappedBy` is used to provide the `RowMapper` class. A row of ResultSet is
usually mapped to a JavaBean, so we define `UserRowMapper` to achieve it:

```
public class UserRowMapper extends BeanRowMapper<User> {}
```

With the power of Java 5 generic programming, nothing is need to do in `UserRowMapper`.

Please note that the fields' names must equal to `User`'s properties' names,
otherwise, you need use `as` for alias:

```
@Unique
@MappedBy(UserRowMapper.class)
@Query("select u.user_id as id, u.user_pwd as password, u.user_name as name from User u where u.user_id=:id")
User queryUser(@Param("id") String id);
```

And last, we are expect one and only one `User` object because we are querying by
primary key `id`, so `@Unique` is used to tell Express-Persist to do some check
and make sure the result of query has one single row, otherwise, DataAccessException
is thrown.

If more `User` objects are need to return, you can define a query method with
returing type of `List` with generic type:

```
@MappedBy(UserRowMapper.class)
@Query("select * from User u order by u.name desc")
List<User> queryUsers();
```

And remember do not put `@Unique` on methods which return `List`.

## Using RowMapper ##

Usually we use BeanRowMapper to map ResultSet to JavaBean. But there are other
RowMappers:

### ObjectArrayRowMapper ###

Mapping ResultSet to `Object[]`. If no `@MappedBy` present, the default RowMapper
is ObjectArrayRowMapper.

### StringRowMapper ###

Mapping ResultSet's first field to `String`.

### IntegerRowMapper ###

Mapping ResultSet's first field to `int`.
