@ECHO  OFF
SET ImPath="..\protos\Im"
SET ImInit="..\protos\Im\__init__.py"
SET LivePath="..\protos\Live"
SET LiveInit="..\protos\Live\__init__.py"
SET ProtoInit="..\protos\__init__.py"
if not exist %ImPath% (md %ImPath%)
if not exist %ImInit% (type nul>%ImInit%)
if not exist %LivePath% (md %LivePath%)
if not exist %LiveInit% (type nul>%LiveInit%)
if not exist %ProtoInit% (type nul>%ProtoInit%)
protoc -Iprotos\Im\Basic -Iprotos\Im\Message -Iprotos\Im\Cloud\Channel -Iprotos\Im\Cloud\Config -Iprotos\Im\Cloud\Data\Update -Iprotos\Im\Cloud\Message -Iprotos\Im\Cloud\Profile -Iprotos\Im\Cloud\Search -Iprotos\Im\Cloud\SessionFolder -Iprotos\Im\Cloud\SessionTag -Iprotos\Im\Cloud\Voice\Call --python_out=..\protos\Im protos\Im\Basic\*.proto protos\Im\Message\*.proto protos\Im\Cloud\Channel\*.proto protos\Im\Cloud\Config\*.proto protos\Im\Cloud\Data\Update\*.proto protos\Im\Cloud\Message\*.proto protos\Im\Cloud\Profile\*.proto protos\Im\Cloud\Search\*.proto protos\Im\Cloud\SessionFolder\*.proto protos\Im\Cloud\SessionTag\*.proto protos\Im\Cloud\Voice\Call\*.proto & protoc -Iprotos\zt.live.interactive --python_out=..\protos\Live protos\zt.live.interactive\*.proto
