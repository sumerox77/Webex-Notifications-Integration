# Webex Github & CircleCI notifier
by sumerox77

## Types of notifications
<section>
There are two types of notifications an end user can get:<br />
The first one is a notification about Pull Requests which is expected to be sent when PR is marked from draft to ready for review<br />

The second type of a notification is for workflows from circleci, this notification will be sent by bot in your private chat with bot. <br />
In order to receive such notification you should confirm that your github email address for PR is set to your working email ( on @cisco.com ) domain.<br />

How to do this:
<br /> `git config --global user.email "<your-email>@cisco.com"`.<br />
To check your credentials: </br> `git config --list`.<br />
[Read more..](https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git)<br />
</section>
