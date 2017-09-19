#!/usr/bin/ksh

#commands to run on Isilon
#/usr/bin/isi status -q
#/usr/bin/isi quota quotas list --exceeded --format=csv --no-header | cut -d"," -f3,5,8
#/usr/bin/isi_for_array -s isi devices | egrep -i "erase|replace"
#/usr/bin/isi events list -w --nodes=n

#tmp out files
rm -f /tmp/isilon_daily_health_check_report*.csv
DATE=`date '+%A_%Y%m%d'`
out=/tmp/isilon_daily_health_check_report_$DATE.csv
isistatus=/tmp/isistatus
isiquota=/tmp/isiquota
faildisk=/tmp/isifaildisk
body=/tmp/isilonbody.txt
hstat=/tmp/isihstat
fnode=/tmp/isifnode
event=/tmp/isievent
hsts=/tmp/isihsts

echo "Hello All," > $hsts
echo " " >> $hsts
echo "Isilon daily health check automated report for `date '+%A_%Y%m%d'`. Please review attachment for details " >> $hsts
echo " " >> $hsts
echo "Cluster_Name      Health_Status " >> $hsts

echo " " > $event
echo "Events list:" >> $event

# "awk '{print $1}' Isilon_Array_list" captures cluster IP address

for i in `awk '{print $1}' Isilon_Array_list`
        do
        ssh root@$i '/usr/bin/isi status -q' > $isistatus
        ssh root@$i '/usr/bin/isi quota quotas list --exceeded --format=csv --no-header | cut -d"," -f3,5,8' > $isiquota
        ssh root@$i '/usr/bin/isi_for_array -s isi devices | egrep -i "erase|replace"' > $faildisk
        Health=`cat $isistatus|grep "Cluster Health:"|awk '{print $4}'|sed 's/]//'`
        Host=`cat $isistatus|grep "Cluster Name:" | cut -d ":" -f2|sed '/^$/d;s/[[:blank:]]//g'`
                cat $isistatus|tail +12|head -n -2| sed 's/[|/]/,/g;s/Totals:/Totals,,/;s/[(]/,/1;s/[)]//1;/^--/d' > $hstat
                cat $hstat | head -n -1| egrep -i -v "OK" | awk -F ',' '{printf "%s", $1}' > $fnode
                fnode1=`cat $fnode`
echo "$Host	$Health$fnode1" >> $hsts
        #Cluster Health Status
        if [ $Health == OK ]
        then
                echo " "
                echo "$Host Health status is $Health"
        else
                echo "$Host Health status is $Health"
                echo "Cluster status in detail"
                echo " "
                echo "Node NO,IP Address,Health,Throughput In,Throughput Out,Throughput total, HDD Storage used,HDD Storage size, HDD Storage percentage, SSD Storage Used/Size"
                #cat $isistatus|tail +12|head -n -2| sed 's/[|/]/,/g;s/Totals:/Totals,,/;s/[(]/,/1;s/[)]//1;/^--/d'
                                cat $hstat
        fi
                fnode2=`cat $fnode|wc -w`
                if [ $fnode2 -gt 0 ]
                then
                    for n in `cat $fnode`
                    do
		    echo " "
                    echo "$Host-$n"
                    ssh root@$i "/usr/bin/isi events list -w --nodes=$n"|sed 1d
                    done
		elif [ $Health != OK ]
	        then
		echo " "
		echo "$Host"
		ssh root@$i "/usr/bin/isi events list -w --severity=critical"|sed 1d 
                fi >> $event
        #Prints OpenFS space
        Capacity=`cat $isistatus|egrep -i Totals: | grep -E -o ".{0,2}%.{0,0}"`
        echo " "
        echo "$Host OpenFS Space is $Capacity used"
        echo " "
        #Exceeded Quotas
        ExceedQ=`cat $isiquota| wc -l`
        if [ $ExceedQ -gt 0 ]
        then
            echo "Exceeded Quotas List"
            echo "Share,Total Size(GBs),Used Size(GBs),Percentage"
        while read line
        do
            Share=`echo $line|awk -F "," '{print $1}'|awk -F "/" '{print $NF}'`
            totalbyt=`echo $line|cut -d "," -f2`
            usedbyt=`echo $line|cut -d "," -f3`
            totalgbs=`echo $totalbyt / 1024 /1024 /1024 | bc;`
            usedgbs=`echo $usedbyt / 1024 /1024 /1024 | bc;`
            percent=$(printf '%i %i' $usedbyt $totalbyt | awk '{ pc=100*$1/$2; i=int(pc); print (pc-i<0.5)?i:i+1 }')
            echo "$Share,$totalgbs,$usedgbs,$percent%"
        done < $isiquota
        else
                echo "No Exceeded Quotas found on the $Host"
        fi
        FailDisk=`cat $faildisk|wc -l`
                if [ $FailDisk -gt 0 ]
                then
                        echo "Faulty Disks on $Host"
                        cat $faildisk|awk '{print $1""$2""$3}' | awk -F "-" '{printf "node-%s\n", $2}'
                        echo " "
                else
                        echo "No Faulty Drives on $Host"
                        echo " "
                fi
done > $out

cat $hsts > $body
cat $event >> $body

mailx -a $out -s "Isilon daily health check report for `date '+%Y-%m-%d'`" user@domain.com < $body

exit 0

