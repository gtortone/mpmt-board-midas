ifndef MIDASSYS
missmidas::
	@echo "...";
	@echo "Missing definition of environment variable 'MIDASSYS' !";
	@echo "...";
endif

INC_DIR   = $(MIDASSYS)/include
LIB_DIR   = $(MIDASSYS)/lib

CC = gcc
CXX = g++
OSFLAGS = -DOS_LINUX -Dextname
CFLAGS = -O3 -Wall -I$(INC_DIR) 
LIB = $(LIB_DIR)/libmidas.a
LIBS = -lm -lz -lutil -lpthread -lrt -lzmq -ldl -lfmt

# use DEBUG=1 to include debugging
ifdef DEBUG
  CFLAGS += -DDEBUG
endif

UFE = mpmtfe

all: $(UFE)

$(UFE): $(LIB) $(LIB_DIR)/mfe.o $(UFE).o mpmtevent.o 
	$(CXX) $(CFLAGS) $(OSFLAGS) -o $(UFE) $(UFE).o $(LIB_DIR)/mfe.o mpmtevent.o $(LIB) $(LIBS)
	strip $(UFE)

%.o: %.cpp
	$(CXX) $(USERFLAGS) $(CFLAGS) $(OSFLAGS) -o $@ -c $<

clean::
	rm -f *.o *~ \#* $(UFE)

