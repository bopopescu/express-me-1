# Binding Parameters #

Express-Persist uses 'named' parameters in SQL statement, and each named
parameter is mapping to the argument according to the `@Param` annotation.
The parameters in SQL statement and all arguments of method are checked by
Express-Persist. If anything goes wrong, DaoConfigException is thrown. For
example, the following definitions are invalid:

```
@Query("select * from User where name=:name")
List<User> queryBy(String name);
```

Because the `@Param("name")` is missing before argument `String name`.

```
@Query("select * from User where name=:name")
List<User> queryBy(@Param("n") String name);
```

Because the value of `@Param("n")` is `n` which is not equal to `name`.

```
@Query("select * from User where name=:name and registerTime>:date")
List<User> queryBy(@Param("name") String name);
```

Because argument which should be mapping to `date` parameter is missing.

# Binding JavaBean #

If the SQL statement takes too many parameters, there are also too many
arguments of method. To reduce the number of arguments, you can binding
JavaBean to SQL parameters like this:

```
@Query("select * from User where name=:u.name and age=:u.age and gender=:u.gender")
List<User> queryByExample(@Param("u") User u);
```

By declaration of `u.name`, `u.age` and `u.gender`, you can pass only one
argument with type `User`, and Express-Persist will automatically bind SQL
parameters as `u.getName()`, `u.getAge()` and `u.getGender()`.