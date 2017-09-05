from netapp_storage import Netapp
while True:
	cmd = input("Enter Command: ")
	if cmd == 'q': quit() 
	x = Netapp()
	y = x.fs_chk(cmd)
	print(y.strip())