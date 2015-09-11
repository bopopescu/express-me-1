# Deploy on Google AppEngine #

It is free to deploy ExpressMe on Google AppEngine. Before you start, make sure
the following software or tools are installed correctly:

  * Java 6 SDK;
  * Google AppEngine SDK for Java.

You can install the latest SUN JDK 6 from http://java.sun.com/javase/downloads/.

You can install the latest Google AppEngine SDK for Java from http://code.google.com/appengine/downloads.html#Google_App_Engine_SDK_for_Java.

## Apply Google AppEngine Account ##

You must have Google AppEngine account. You can [register for free](http://appengine.google.com).

## Create Google AppEngine Application ##

Once you are signed in Google AppEngine, you can create an application:

![http://express-me.googlecode.com/svn/wiki/ExpressMe-CreateApp.png](http://express-me.googlecode.com/svn/wiki/ExpressMe-CreateApp.png)

Please note that the `Application Identifier` is your application id as well as
your application's domain name like `my-app-id.appspot.com`.

## Deploy ExpressMe on Google AppEngine ##

Download ExpressMe from: http://express-me.googlecode.com/files/express-me.zip.

Unzip the file and get the `war` directory.

Edit `war/WEB-INF/appengine-web.xml` using any text editor, and change the
`<application>express-me</application>` to your application id like
`<application>my-app-id</application>`:

![http://express-me.googlecode.com/svn/wiki/ExpressMe-ChangeAppId.png](http://express-me.googlecode.com/svn/wiki/ExpressMe-ChangeAppId.png)

Assume that ExpressMe is unzip to `C:\war`, then open command window and using
`appcfg.cmd` to deploy the application:

![http://express-me.googlecode.com/svn/wiki/ExpressMe-Appcfg.png](http://express-me.googlecode.com/svn/wiki/ExpressMe-Appcfg.png)

When prompt input the email and password, enter your google account and password.

If you want to use proxy, using `-p` option:

```
appcfg.cmd -p proxy-server:8080 update war
```