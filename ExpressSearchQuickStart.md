# Quick Start #

You can get the source code of Express-Search from
http://express-me.googlecode.com/svn/trunk/ExpressSearch. Run ant to build the
project and get the `express-search.jar` in `dist` directory. Or you can download
from http://code.google.com/p/express-me/downloads/list?q=Express-Search.

# Overview #

Suppose we have a Post object which represent posts published by users. It has 5 properties of 'id', 'title', 'userId', 'content' and 'createTime', and the primary key is 'id' which identify the unique Post object.

```
// file: Post.java
import org.expressme.search.Index;
import org.expressme.search.SearchableId;
import org.expressme.search.SearchableProperty;
import org.expressme.search.Store;

public class Post {

    private String id;
    private String title;
    private String userId;
    private String content;
    private long createTime;

    @SearchableId
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    @SearchableProperty(index=Index.ANALYZED, store=Store.YES, boost=5.0f)
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    @SearchableProperty(index=Index.NO, store=Store.YES)
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    @SearchableProperty(index=Index.ANALYZED, store=Store.YES)
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    @SearchableProperty(index=Index.NO, store=Store.YES)
    public long getCreateTime() { return createTime; }
    public void setCreateTime(long createTime) { this.createTime = createTime; }

}
```

A searchable object may have many properties, but must have one and only one property that marked as "SearchableId", which is usually the primary key in database. Other properties which need to be searched or stored must be marked as "SearchableProperty".

SearchableProperty has 'index' and 'store' values.

The value of 'index' can be:

  * Index.ANALYZED: This property will be analyzed and can be searched. For example, "I like apples" will be analyzed as 3 words: "I", "like", "apples", and each word can be searched.
  * Index.NOT\_ANALYZED: This property will not be analyzed but can be searched. For example, "I like apples" will not be analyzed, but be treat as one word, so it cannot be searched by "I", "like" or "apples", but it can be searched by "I like apples".
  * Index.NO: This property will not be analyzed and cannot be searched.

The value of 'store' can be:

  * Store.YES: This property will be stored in Lucene index store, so it can be retrieved when searching.
  * Store.NO: This property will not be stored in Lucene index store, so it cannot be retrieved when searching, and must retrieve this property from database or somewhere else.
  * Store.COMPRESS: The same as Store.YES, but compressed to save disk space.

We need to create `Searcher<Post>` instance:

```
Searcher<Post> createSearcher() {
    SearcherImpl<Post> searcher = new SearcherImpl<Post>();
    searcher.setAnalyzer(new org.apache.lucene.analysis.standard.StandardAnalyzer());
    searcher.setDirectory(org.apache.lucene.store.FSDirectory.getDirectory("/var/search/")); // must be writable!
    searcher.setDocumentMapper(new DocumentMapper<Post>(Post.class));
    searcher.setFormatter(new org.apache.lucene.search.highlight.SimpleHTMLFormatter("<b>", "</b>"));
    searcher.init();
    return searcher;
}
```

Now you can use `searcher` instance for search now.

To index a Post object (make it searchable), using:

```
Post post = ... // loaded from database or somewhere else
searcher.index(post);
```

To unindex a Post object (make it unsearchable), using:

```
Post post = ... // loaded from database or somewhere else
searcher.unindex(post);
```

And do search with keywords:

```
// search for top 10 results:
List<Post> results = searcher.search("my keyword", 0, 10);
```

If you want to know more details about Express-Search, see [Developer's Guide](ExpressSearchDeveloper.md).