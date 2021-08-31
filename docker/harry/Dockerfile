FROM maven:3-openjdk-11 as builder

# cassandra-harry doesn't have an official Apache distribution yet;
# we have to build it from the source, here we pin it to a known commit hash
ENV GIT_ID="f569b94cdfc41b241e970880a3d4dbbce92c652a"

RUN git clone https://github.com/grighetto/cassandra-harry.git cassandra-harry; \
	cd cassandra-harry; \
	git checkout $GIT_ID

WORKDIR /cassandra-harry
RUN mvn -pl '!harry-integration' clean install -DskipTests

FROM adoptopenjdk/openjdk11

RUN apt-get update
RUN apt-get install -y gettext-base

WORKDIR /cassandra-harry

COPY --from=builder /cassandra-harry/harry-integration-external/target/harry-integration-external-0.0.1-SNAPSHOT.jar .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]