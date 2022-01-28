
# Target
BIN_DIR = bin
BIN = $(BIN_DIR)/evproducer

# Match all sources in src direcotry
SRCS_DIR = src
SRCS = $(wildcard $(SRCS_DIR)/**/*.cpp $(SRCS_DIR)/*.cpp)

# Builds object list from sources, substitues .cpp for .o
OBJS_DIR = obj
OBJS = $(patsubst $(SRCS_DIR)/%.cpp,$(OBJS_DIR)/%.o,$(SRCS))

# Include headers files
INCLUDE_DIRS = include
INCLUDE = $(foreach includedir,$(INCLUDE_DIRS),-I$(includedir))

# Search libraries in following directories
INCLUDE_LIB_DIRS = 
INCLUDE_LIB = $(foreach includedir,$(INCLUDE_LIB_DIRS),-L$(includedir))

# Set compiler, preprocesor and linker flags
CXXFLAGS += -std=c++17 -Wall -Wno-unused-result
# CXXFLAGS += -O3
LDFLAGS += $(INCLUDE_LIB)
LDLIBS += -lzmq -lfmt -lstdc++fs

# use DEBUG=1 to include debugging
ifdef DEBUG
  CXXFLAGS += -g	
endif

# Set other tools
MKDIR = mkdir -p

# Avoid filename conflicts
.PHONY: all clean

# Rules
all: $(BIN)

$(OBJS_DIR)/%.o: $(SRCS_DIR)/%.cpp
	@$(MKDIR) $(dir $@)
	$(CXX) $(CXXFLAGS) -I$(INCLUDE_DIRS) -c $< -o $@

$(BIN): $(OBJS)
	@$(MKDIR) $(dir $@)
	$(CXX) $(LDFLAGS) $^ $(LDLIBS) -o $@
	strip $(BIN) 

clean:
	@$(RM) $(BIN)
	@$(RM) $(OBJS)
