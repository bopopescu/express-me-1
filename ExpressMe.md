_To be updated_

# Introduction #

ExpressMe is an open source blog system written by Java. ExpressMe can be run on
any JavaEE server including Tomcat, Resin, Jetty, GlassFish, WebLogic, etc.
ExpressMe can also run on Google AppEngine! See more [features](ExpressMeFeature.md).

You can [download for free](ExpressMeDownload.md).

# Sub-projects #

ExpressMe is build on modules, and its sub-projects can be reused in any other
Java projects:

## [WebWind](http://webwind.googlecode.com/) ##

A MVC framework which support friendly URL like `/blog/display/20080909` and
agile web development.

## [Express-Persist](ExpressPersist.md) ##

A persistence framework which enables creating DAO without JDBC.

## [Express-Search](ExpressSearch.md) ##

A full-text search framework build on [Apache Lucene](http://lucene.apache.org/)
but with very simple APIs.