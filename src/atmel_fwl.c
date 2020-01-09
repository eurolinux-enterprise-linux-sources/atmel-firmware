/*** -*- linux-c -*- **********************************************************

     Firmware loader for Atmel at76c502 at76c504 and at76c506 wireless cards.

            Copyright 2003 Simon Kelley.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This software is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Atmel wireless lan drivers; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

******************************************************************************/

#include <stdio.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>

#define ATMELFWL 0x8be0
#define ATMELIDIFC 0x8be1
#define ATMELMAGIC 0x51807

struct atmel_priv_ioctl {
	char id[32];
	unsigned char *data; 
	unsigned short len;    
};

main(int argc, char **argv)
{
	int i, magic, rc, sock = -1;
	struct ifreq ifr;
	struct atmel_priv_ioctl com;
	static const int families[] = {
		AF_INET, AF_IPX, AF_AX25, AF_APPLETALK
	};
	FILE *file;
	char *id;
	long len;

	if (argc != 3) {
		fprintf(stderr, 
			"Usage: atmel_fwl <interface> <path/to/firmware>\n");
		exit(1);
	}
	
	if (!(file = fopen(argv[2], "r"))) {
		fprintf(stderr,
			"atmel_fw: Cannot open %s:%s\n", 
			argv[2], strerror(errno) );
		exit(1);
	}
			
	if (fseek(file, 0, SEEK_END) != 0) {
		perror("atmel_fwl: cannot seek to end");
		exit(1);
	}
	if ((len = ftell(file)) == -1) {
		perror("atmel_fwl: cannot get file length");
		exit(1);
	}
	com.len = len;
	rewind(file);
	if (!(com.data = malloc(com.len))) {
		fprintf(stderr, "atmel_fwl: cannot get memory.\n");
		exit(1);
	}
	if (fread(com.data, 1, com.len, file) != com.len) {
		fprintf(stderr, "atmel_fwl: cannot read file.\n");
		exit(1);
	}
	fclose(file);

	if (id = strrchr(argv[2], '/'))
		id++;
	else
		id = argv[2];

	strncpy(com.id, id, 31);
	com.id[31] = '\0';
		
   	/*
	 * Now pick any (existing) useful socket family for generic queries
	 * Note : don't open all the socket, only returns when one matches,
	 * all protocols might not be valid.
	 * Workaround by Jim Kaba <jkaba@sarnoff.com>
	 * Note : in 99% of the case, we will just open the inet_sock.
	 * The remaining 1% case are not fully correct...
	 */
	
	/* Try all families we support */
	for(i = 0; i < sizeof(families)/sizeof(int); ++i) {
		/* Try to open the socket, if success returns it */
		sock = socket(families[i], SOCK_DGRAM, 0);
		if(sock >= 0)
			break;
	}

	if (sock == -1) {
		perror("atmel_fwl: cannot get socket");
		exit(1);
	}
	
	strcpy(ifr.ifr_ifrn.ifrn_name, argv[1]);
  	rc = ioctl(sock, ATMELIDIFC, &ifr);
	if (rc !=0 || ifr.ifr_ifru.ifru_ivalue != ATMELMAGIC) {
		fprintf(stderr, "atmel_fwl: %s is not an Atmel interface.\n");
		exit(1);
	}

	ifr.ifr_ifru.ifru_data = (char *)&com;
	rc = ioctl(sock, ATMELFWL, &ifr);
	if (rc != 0) {
		perror("atmel_fwl: Cannot load firmware");
		exit(1);
	}

	exit(0);
}



