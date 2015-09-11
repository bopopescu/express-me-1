# Using Batch #

To improve JDBC operation with lots of data, experienced developers will use
batch update. Express-Persist also supports batch, but needs a little more work.

To make a DAO support batch, just let it extends `BatchSupport`:

```
public class UserDao extends BatchSupport {

    @Update("update User set name=:name where id=:id")
    void updateUserName(@Param("id") String id, @Param("name") String name);
}
```

And write your batch code:

```
try {
    dao.prepareBatch();
    // now the batch prepared:
    dao.updateUserName("id-1", "change A's name");
    dao.updateUserName("id-2", "change B's name");
    dao.updateUserName("id-3", "change C's name");
    // execute:
    int[] results = dao.executeBatch();
}
finally {
    dao.closeBatch();
}
```

Using `try ... finally ...` to make sure the underlying JDBC resources is cleanup.
Please remember that once `prepareBatch()` is called, the database will not change
during the DAO operations until the `executeBatch()` is called. The `closeBatch()`
is used to cleanup JDBC resources, so it MUST be placed in `finally { ... }`.