Name: Mohammad Saim Jamal
ID: MSJ2150

Written in PYTHON
This contains only gbnnode, which simulates GBN protocol for packet loss.

I made a GBNProtocol object, which ran its own methods using my created packet object.
I used the pickle class to make the packet byte-like to send it through a socket.
I used multithreading to get rid of the headache of having to keep track of which
packets have been ack'd currently, only keeping track of the most closest number
to the one known ack'd.

You startup the program using
> python3 gbnnode.py <YOUR PORT> <RECEIVER PORT> <WINDOW_SIZE> <-p or -d> <probability>
then, use the SEND command (the only command) to send messages to the receiver.
