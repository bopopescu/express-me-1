# Limited Query #

Sometimes you may only want to return limited number of results from SQL query.
Express-Persist provides two annotations `@FirstResult` and `@MaxResults` to
achieve it. The only work to do is put it in an int-type argument in method
declaration:

```
@MappedBy(UserRowMapper.class)
@Query("select * from User u order by u.id")
List<User> queryFrom(@FirstResult int first);

@MappedBy(UserRowMapper.class)
@Query("select * from User u order by u.id")
List<User> queryMax(@MaxResults int max);

@MappedBy(UserRowMapper.class)
@Query("select * from User u order by u.id")
List<User> queryRange(@FirstResult int first, @MaxResults int max);
```

You can use both or only one of them. If no @FirstResult is specified, the
default first result is 0. If no @MaxResults is specified, the default max
results is `Integer.MAX_VALUE`.

For example, the database table has following data:

| **id** | **name** |
|:-------|:---------|
| 0      | user-0   |
| 1      | user-1   |
| 2      | user-2   |
| 3      | user-3   |
| 4      | user-4   |
| 5      | user-5   |
| 6      | user-6   |
| 7      | user-7   |
| 8      | user-8   |
| 9      | user-9   |

When you call `queryFrom(@FirstResult int)` with:

queryFrom(0): user-0, user-1, user-2, user-3, user-4, user-5, user-6, user-7, user-8, user-9.

queryFrom(5): user-5, user-6, user-7, user-8, user-9.

queryFrom(10): (empty result)

queryFrom(-1): DataAccessException

When you call `queryMax(@MaxResults int)` with:

queryMax(10): user-0, user-1, user-2, user-3, user-4, user-5, user-6, user-7, user-8, user-9.

queryMax(5): user-0, user-1, user-2, user-3, user-4.

queryMax(0): (empty result)

queryMax(-1): DataAccessException

When you call `queryRange(@FirstResult int, @MaxResults int)` with:

queryRange(0, 5): user-0, user-1, user-2, user-3, user-4.

queryRange(5, 5): user-5, user-6, user-7, user-8, user-9.

queryRange(7, 5): user-7, user-8, user-9.

queryRange(7, 0): (empty result)