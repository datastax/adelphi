FROM maven:3-openjdk-11 as builder

# cassandra-diff doesn't have an official Apache distribution yet;
# we have to build it from the source, here we pin it to a known commit hash
ENV GIT_ID="4c9bc4f4e3fd7d23b1284c89266ffbf10b8f0183"

RUN git clone https://github.com/apache/cassandra-diff.git cassandra-diff; \
	cd cassandra-diff; \
	git checkout $GIT_ID

WORKDIR /cassandra-diff
RUN mvn clean package -DskipTests

FROM adelphi-dev/spark:3.0.0

COPY --from=builder /cassandra-diff/spark-uberjar/target/spark-uberjar-0.2-SNAPSHOT.jar /opt/spark/jars