# Using Update #

You can execute SQL statements of `INSERT`, `UPDATE` and `DELETE` by `@Update`
annotation in Express-Persist:

```
@Update("insert into User(id, password, name) values(:u.id, :u.password, :u.name)")
void createUser(@Param("u") User user);
```

`INSERT` statement always takes many parameters, so it is a good idea to
[bind JavaBean](ExpressPersistBind#Binding_JavaBean.md) as argument.

`UPDATE` statement is the same like `INSERT` statement:

```
@Update("update User set password=:u.password, name=:u.name where id=:u.id")
void updateUser(@Param("u") User user);
```

`DELETE` statement is simple:

```
@Update("delete User where id=:id")
int deleteUser(@Param("id") String id);
```

Please note that the returning type of method with `@Update` **MUST** be `void`
or `int`. You can get the affected rows by returning `int`.