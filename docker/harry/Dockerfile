FROM maven:3-openjdk-11 as builder

# cassandra-harry doesn't have an official Apache distribution yet;
# we have to build it from the source, here we pin it to a known commit hash
ENV GIT_ID="252dc6c4101e8ee631a27e5435d302853a7ad219"

RUN git clone https://github.com/grighetto/cassandra-harry.git cassandra-harry; \
	cd cassandra-harry; \
	git checkout $GIT_ID

WORKDIR /cassandra-harry
RUN mvn -pl '!harry-integration' clean install -DskipTests

FROM adoptopenjdk/openjdk11

COPY --from=builder /cassandra-harry