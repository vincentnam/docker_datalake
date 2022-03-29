FROM openjdk:11

ENV SBT_VERSION 1.5.5

RUN curl -L -o sbt-$SBT_VERSION.zip https://github.com/sbt/sbt/releases/download/v$SBT_VERSION/sbt-$SBT_VERSION.zip
RUN unzip sbt-$SBT_VERSION.zip -d ops

USER root

COPY /certificate/neocampus-datalake-mongodb.dev.modiscloud.net.pem $JAVA_HOME/lib/security
COPY /certificate/neocampus-datalake-swift.dev.modiscloud.net.pem $JAVA_HOME/lib/security

RUN cd $JAVA_HOME/lib/security
RUN keytool -importcert -trustcacerts -alias mongodb-datalake -file $JAVA_HOME/lib/security/neocampus-datalake-mongodb.dev.modiscloud.net.pem -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit -noprompt
RUN keytool -importcert -trustcacerts -alias swift-datalake -file $JAVA_HOME/lib/security/neocampus-datalake-swift.dev.modiscloud.net.pem -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit -noprompt
WORKDIR project

ADD . /project

RUN /ops/sbt/bin/sbt compile
CMD /ops/sbt/bin/sbt run