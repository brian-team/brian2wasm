PROGRAM = main.html

SRCS = {{source_files}}
H_SRCS = {{header_files}}
OBJS = ${SRCS:.cpp=.o}
OPTIMISATIONS = {{ compiler_flags }}
CXXFLAGS = -c -Wno-write-strings $(OPTIMISATIONS) -I. {{ openmp_pragma('compilation') }} {{ compiler_debug_flags }}
LFLAGS = {{ openmp_pragma('compilation') }} {{ linker_flags }} {{ linker_debug_flags }} --emrun
DEPS = make.deps

all: $(PROGRAM)

.PHONY: all clean

$(PROGRAM): $(OBJS) $(DEPS) makefile
	emcc $(OBJS) -o $(PROGRAM) $(LFLAGS)

clean:
	{{ rm_cmd }}

make.deps: $(SRCS) $(H_SRCS)
	emcc $(CXXFLAGS) -MM $(SRCS) > make.deps
	
ifneq ($(wildcard $(DEPS)), )
include $(DEPS)
endif

%.o : %.cpp makefile
	emcc $(CXXFLAGS) $< -o $@
