#   Licensed to the Apache Software Foundation (ASF) under one
#   or more contributor license agreements.  See the NOTICE file
#   distributed with this work for additional information
#   regarding copyright ownership.  The ASF licenses this file
#   to you under the Apache License, Version 2.0 (the
#   "License"); you may not use this file except in compliance
#   with the License.  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
echo $1
CONFIG_FILE=$1
cat $CONFIG_FILE
OUTPUT_DIR=$2
CLUSTER_STATE_DIR=/cassandra-harry/cluster-state

# Replace env vars into a new config file
envsubst < $CONFIG_FILE > /cassandra-harry/config.yaml
CONFIG_FILE=/cassandra-harry/config.yaml

java -ea \
     -Xms4g \
     -Xmx4g \
     -XX:MaxRAM=4g \
     -XX:MaxMetaspaceSize=384M \
     -XX:MetaspaceSize=128M \
     -XX:SoftRefLRUPolicyMSPerMB=0 \
     -XX:MaxDirectMemorySize=2g \
     -Dcassandra.memtable_row_overhead_computation_step=100 \
     -Djdk.attach.allowAttachSelf=true \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:-UseBiasedLocking \
     -XX:+UseTLAB \
     -XX:+ResizeTLAB \
     -XX:+UseNUMA \
     -XX:+PerfDisableSharedMem \
     -XX:+UseConcMarkSweepGC \
     -XX:+CMSParallelRemarkEnabled \
     -XX:SurvivorRatio=8 \
     -XX:MaxTenuringThreshold=1 \
     -XX:CMSInitiatingOccupancyFraction=75 \
     -XX:+UseCMSInitiatingOccupancyOnly \
     -XX:CMSWaitDuration=10000 \
     -XX:+CMSParallelInitialMarkEnabled \
     -XX:+CMSEdenChunksRecordAlways \
     -XX:+CMSClassUnloadingEnabled \
     -XX:+UseCondCardMark \
     -XX:OnOutOfMemoryError=kill \
     --add-exports java.base/jdk.internal.misc=ALL-UNNAMED \
     --add-exports java.base/jdk.internal.ref=ALL-UNNAMED \
     --add-exports java.base/sun.nio.ch=ALL-UNNAMED \
     --add-exports java.management.rmi/com.sun.jmx.remote.internal.rmi=ALL-UNNAMED \
     --add-exports java.rmi/sun.rmi.registry=ALL-UNNAMED \
     --add-exports java.rmi/sun.rmi.server=ALL-UNNAMED \
     --add-exports java.sql/java.sql=ALL-UNNAMED \
     --add-opens java.base/java.lang.module=ALL-UNNAMED \
     --add-opens java.base/jdk.internal.loader=ALL-UNNAMED \
     --add-opens java.base/jdk.internal.ref=ALL-UNNAMED \
     --add-opens java.base/jdk.internal.reflect=ALL-UNNAMED \
     --add-opens java.base/jdk.internal.math=ALL-UNNAMED \
     --add-opens java.base/jdk.internal.module=ALL-UNNAMED \
     --add-opens java.base/jdk.internal.util.jar=ALL-UNNAMED \
     --add-opens jdk.management/com.sun.management.internal=ALL-UNNAMED \
     -Dharry.root=${CLUSTER_STATE_DIR} \
     -Dlogback.configurationFile=logback-dtest.xml \
     -jar harry-integration-external-0.0.1-SNAPSHOT.jar \
     ${CONFIG_FILE}

if [ $? -ne 0 ]; then
  if [ -e "failure.dump" ]; then
    echo "Creating failure dump..."
    RUN="run-$(date +%Y%m%d%H%M%S)-${RANDOM}"
    mkdir ${OUTPUT_DIR}
    mkdir ${OUTPUT_DIR}/cluster-state
    mv ${CLUSTER_STATE_DIR}* ${OUTPUT_DIR}/cluster-state
    mv operation.log ${OUTPUT_DIR}/
    mv failure.dump ${OUTPUT_DIR}/
    mv run.yaml ${OUTPUT_DIR}/
  fi
fi
