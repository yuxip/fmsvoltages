#!/bin/bash
t=`date +%Y.%h.%d-%H.%d.%S`
(
sleep 2;
echo -e "\r";
sleep 1;
echo -e "read (0-15,0-15) \r";
sleep 5;
echo -e "set voltage limit 1600 \r";
echo -e "\r";
echo -e "write (0-15,0-15) -900\r"; sleep 2;

echo -e "write (0,0) -1569\r"; sleep 2;
echo -e "write (0,1) -1433\r"; sleep 2;
echo -e "write (0,2) -1418\r"; sleep 2;
echo -e "write (0,3) -1488\r"; sleep 2;
echo -e "write (0,4) -1536\r"; sleep 2;
echo -e "write (0,5) -1569\r"; sleep 2;
echo -e "write (0,6) -1435\r"; sleep 2;
echo -e "write (0,9) -1579\r"; sleep 2;
echo -e "write (0,10) -1502\r"; sleep 2;
echo -e "write (0,11) -1416\r"; sleep 2;
echo -e "write (0,12) -1502\r"; sleep 2;
echo -e "write (0,13) -1533\r"; sleep 2;
echo -e "write (0,14) -1588\r"; sleep 2;
echo -e "write (1,0) -1529\r"; sleep 2;
echo -e "write (1,1) -1490\r"; sleep 2;
echo -e "write (1,2) -1565\r"; sleep 2;
echo -e "write (1,3) -1420\r"; sleep 2;
echo -e "write (1,4) -1478\r"; sleep 2;
echo -e "write (1,5) -1566\r"; sleep 2;
echo -e "write (1,6) -1417\r"; sleep 2;
echo -e "write (1,9) -1537\r"; sleep 2;
echo -e "write (1,10) -1537\r"; sleep 2;
echo -e "write (1,11) -1415\r"; sleep 2;
echo -e "write (1,12) -1555\r"; sleep 2;
echo -e "write (1,13) -1516\r"; sleep 2;
echo -e "write (1,14) -1494\r"; sleep 2;
echo -e "write (2,0) -1362\r"; sleep 2;
echo -e "write (2,1) -1421\r"; sleep 2;
echo -e "write (2,2) -1498\r"; sleep 2;
echo -e "write (2,3) -1500\r"; sleep 2;
echo -e "write (2,4) -1598\r"; sleep 2;
echo -e "write (2,5) -1589\r"; sleep 2;
echo -e "write (2,6) -1508\r"; sleep 2;
echo -e "write (2,9) -1512\r"; sleep 2;
echo -e "write (2,10) -1536\r"; sleep 2;
echo -e "write (2,11) -1577\r"; sleep 2;
echo -e "write (2,12) -1500\r"; sleep 2;
echo -e "write (2,14) -1548\r"; sleep 2;
echo -e "write (3,0) -1433\r"; sleep 2;
echo -e "write (3,1) -1519\r"; sleep 2;
echo -e "write (3,2) -1463\r"; sleep 2;
echo -e "write (3,3) -1485\r"; sleep 2;
echo -e "write (3,4) -1435\r"; sleep 2;
echo -e "write (3,5) -1573\r"; sleep 2;
echo -e "write (3,6) -1463\r"; sleep 2;
echo -e "write (3,9) -1426\r"; sleep 2;
echo -e "write (3,10) -1362\r"; sleep 2;
echo -e "write (3,11) -1396\r"; sleep 2;
echo -e "write (3,12) -1493\r"; sleep 2;
echo -e "write (3,13) -1498\r"; sleep 2;
echo -e "write (3,14) -1497\r"; sleep 2;
echo -e "write (4,0) -1544\r"; sleep 2;
echo -e "write (4,1) -1479\r"; sleep 2;
echo -e "write (4,2) -1491\r"; sleep 2;
echo -e "write (4,3) -1397\r"; sleep 2;
echo -e "write (4,4) -1566\r"; sleep 2;
echo -e "write (4,5) -1490\r"; sleep 2;
echo -e "write (4,6) -1445\r"; sleep 2;
echo -e "write (4,9) -1389\r"; sleep 2;
echo -e "write (4,10) -1543\r"; sleep 2;
echo -e "write (4,11) -1494\r"; sleep 2;
echo -e "write (4,12) -1559\r"; sleep 2;
echo -e "write (4,13) -1490\r"; sleep 2;
echo -e "write (4,14) -1565\r"; sleep 2;
echo -e "write (5,0) -1557\r"; sleep 2;
echo -e "write (5,1) -1600\r"; sleep 2;
echo -e "write (5,2) -1395\r"; sleep 2;
echo -e "write (5,3) -1591\r"; sleep 2;
echo -e "write (5,4) -1556\r"; sleep 2;
echo -e "write (5,5) -1409\r"; sleep 2;
echo -e "write (5,6) -1596\r"; sleep 2;
echo -e "write (5,9) -1454\r"; sleep 2;
echo -e "write (5,10) -1566\r"; sleep 2;
echo -e "write (5,11) -1528\r"; sleep 2;
echo -e "write (5,12) -1511\r"; sleep 2;
echo -e "write (5,13) -1565\r"; sleep 2;
echo -e "write (5,14) -1588\r"; sleep 2;
echo -e "write (6,0) -1550\r"; sleep 2;
echo -e "write (6,1) -1537\r"; sleep 2;
echo -e "write (6,2) -1440\r"; sleep 2;
echo -e "write (6,3) -1395\r"; sleep 2;
echo -e "write (6,4) -1569\r"; sleep 2;
echo -e "write (6,5) -1557\r"; sleep 2;
echo -e "write (6,6) -1374\r"; sleep 2;
echo -e "write (6,9) -1467\r"; sleep 2;
echo -e "write (6,10) -1369\r"; sleep 2;
echo -e "write (6,12) -1365\r"; sleep 2;
echo -e "write (6,13) -1390\r"; sleep 2;
echo -e "write (6,14) -1500\r"; sleep 2;
echo -e "write (7,0) -1480\r"; sleep 2;
echo -e "write (7,1) -1515\r"; sleep 2;
echo -e "write (7,2) -1515\r"; sleep 2;
echo -e "write (7,3) -1384\r"; sleep 2;
echo -e "write (7,4) -1571\r"; sleep 2;
echo -e "write (7,5) -1565\r"; sleep 2;
echo -e "write (7,6) -1510\r"; sleep 2;
echo -e "write (7,9) -1565\r"; sleep 2;
echo -e "write (7,10) -1555\r"; sleep 2;
echo -e "write (7,11) -1492\r"; sleep 2;
echo -e "write (7,12) -1575\r"; sleep 2;
echo -e "write (7,13) -1493\r"; sleep 2;
echo -e "write (7,14) -1510\r"; sleep 2;
echo -e "write (8,0) -1578\r"; sleep 2;
echo -e "write (8,1) -1443\r"; sleep 2;
echo -e "write (8,2) -1411\r"; sleep 2;
echo -e "write (8,3) -1590\r"; sleep 2;
echo -e "write (8,4) -1481\r"; sleep 2;
echo -e "write (8,5) -1499\r"; sleep 2;
echo -e "write (8,6) -1281\r"; sleep 2;
echo -e "write (8,9) -1440\r"; sleep 2;
echo -e "write (8,10) -1518\r"; sleep 2;
echo -e "write (8,11) -1412\r"; sleep 2;
echo -e "write (8,12) -1502\r"; sleep 2;
echo -e "write (8,13) -1409\r"; sleep 2;
echo -e "write (8,14) -1515\r"; sleep 2;
echo -e "write (9,0) -1539\r"; sleep 2;
echo -e "write (9,1) -1590\r"; sleep 2;
echo -e "write (9,2) -1589\r"; sleep 2;
echo -e "write (9,3) -1497\r"; sleep 2;
echo -e "write (9,4) -1502\r"; sleep 2;
echo -e "write (9,5) -1461\r"; sleep 2;
echo -e "write (9,6) -1544\r"; sleep 2;
echo -e "write (9,9) -1417\r"; sleep 2;
echo -e "write (9,10) -1437\r"; sleep 2;
echo -e "write (9,11) -1592\r"; sleep 2;
echo -e "write (9,12) -1585\r"; sleep 2;
echo -e "write (9,13) -1410\r"; sleep 2;
echo -e "write (9,14) -1576\r"; sleep 2;
echo -e "write (10,0) -1544\r"; sleep 2;
echo -e "write (10,1) -1410\r"; sleep 2;
echo -e "write (10,2) -1593\r"; sleep 2;
echo -e "write (10,3) -1569\r"; sleep 2;
echo -e "write (10,4) -1412\r"; sleep 2;
echo -e "write (10,5) -1565\r"; sleep 2;
echo -e "write (10,6) -1489\r"; sleep 2;
echo -e "write (10,9) -1533\r"; sleep 2;
echo -e "write (10,10) -1538\r"; sleep 2;
echo -e "write (10,11) -1419\r"; sleep 2;
echo -e "write (10,12) -1490\r"; sleep 2;
echo -e "write (10,13) -1496\r"; sleep 2;
echo -e "write (10,14) -1555\r"; sleep 2;
echo -e "write (11,0) -1478\r"; sleep 2;
echo -e "write (11,1) -1570\r"; sleep 2;
echo -e "write (11,2) -1426\r"; sleep 2;
echo -e "write (11,3) -1445\r"; sleep 2;
echo -e "write (11,4) -1198\r"; sleep 2;
echo -e "write (11,5) -1489\r"; sleep 2;
echo -e "write (11,6) -1546\r"; sleep 2;
echo -e "write (11,9) -1498\r"; sleep 2;
echo -e "write (11,10) -1558\r"; sleep 2;
echo -e "write (11,11) -1525\r"; sleep 2;
echo -e "write (11,12) -1421\r"; sleep 2;
echo -e "write (11,13) -1514\r"; sleep 2;
echo -e "write (11,14) -1580\r"; sleep 2;
echo -e "write (12,0) -1505\r"; sleep 2;
echo -e "write (12,1) -1489\r"; sleep 2;
echo -e "write (12,2) -1437\r"; sleep 2;
echo -e "write (12,3) -1479\r"; sleep 2;
echo -e "write (12,4) -1553\r"; sleep 2;
echo -e "write (12,5) -1492\r"; sleep 2;
echo -e "write (12,6) -1343\r"; sleep 2;
echo -e "write (12,9) -1318\r"; sleep 2;
echo -e "write (12,10) -1308\r"; sleep 2;
echo -e "write (12,11) -1220\r"; sleep 2;
echo -e "write (12,12) -1380\r"; sleep 2;
echo -e "write (12,13) -1331\r"; sleep 2;
echo -e "write (12,14) -1314\r"; sleep 2;
echo -e "write (13,0) -1496\r"; sleep 2;
echo -e "write (13,1) -1546\r"; sleep 2;
echo -e "write (13,2) -1549\r"; sleep 2;
echo -e "write (13,3) -1436\r"; sleep 2;
echo -e "write (13,4) -1340\r"; sleep 2;
echo -e "write (13,5) -1436\r"; sleep 2;
echo -e "write (13,6) -1450\r"; sleep 2;
echo -e "write (13,9) -1570\r"; sleep 2;
echo -e "write (13,10) -1462\r"; sleep 2;
echo -e "write (13,11) -1530\r"; sleep 2;
echo -e "write (13,12) -1510\r"; sleep 2;
echo -e "write (13,13) -1313\r"; sleep 2;
echo -e "write (13,14) -1496\r"; sleep 2;
echo -e "write (14,0) -1417\r"; sleep 2;
echo -e "write (14,1) -1533\r"; sleep 2;
echo -e "write (14,2) -1542\r"; sleep 2;
echo -e "write (14,3) -1570\r"; sleep 2;
echo -e "write (14,4) -1277\r"; sleep 2;
echo -e "write (14,5) -1550\r"; sleep 2;
echo -e "write (14,6) -1462\r"; sleep 2;
echo -e "write (14,9) -1446\r"; sleep 2;
echo -e "write (14,10) -1471\r"; sleep 2;
echo -e "write (14,11) -1482\r"; sleep 2;
echo -e "write (14,12) -1432\r"; sleep 2;
echo -e "write (14,13) -1493\r"; sleep 2;
echo -e "write (14,14) -1565\r"; sleep 2;
echo -e "write (15,0) -1531\r"; sleep 2;
echo -e "write (15,1) -1526\r"; sleep 2;
echo -e "write (15,2) -1567\r"; sleep 2;
echo -e "write (15,15) -1480\r"; sleep 2;

sleep 2;
echo -e "read (0-15,0-15)\r";
sleep 10;
echo -e "\r";
echo -e "\r";
echo -e "^]";
sleep 1;
) | telnet fms-serv.trg.bnl.local 7008 > ../hvlog_run11/fms_hv2_7008_$t.tex
echo Set new HV
cat ../hvlog_run11/fms_hv2_7008_$t.tex
