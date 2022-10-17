PROGRAM = wasm_module.js

SRCS = {{source_files}}
H_SRCS = {{header_files}}
OBJS = ${SRCS:.cpp=.o}
OPTIMISATIONS = {{ compiler_flags }}
CXXFLAGS = -c -Wno-write-strings $(OPTIMISATIONS) -I. {{ openmp_pragma('compilation') }} {{ compiler_debug_flags }} -fwasm-exceptions 
LFLAGS = {{ openmp_pragma('compilation') }} {{ linker_flags }} {{ linker_debug_flags }} -fwasm-exceptions -sALLOW_MEMORY_GROWTH
all: $(PROGRAM)

.PHONY: all clean

$(PROGRAM): $(OBJS) $(DEPS) makefile {{ preamble_file }}
	emcc $(OBJS) -o $(PROGRAM) $(LFLAGS) {{ preloads }} --pre-js {{ preamble_file }} -s MODULARIZE --js-library brian_library.js -s ENVIRONMENT=worker

clean:
	{{ rm_cmd }}

make.deps: $(SRCS) $(H_SRCS)
	emcc $(CXXFLAGS) -MM $(SRCS) > make.deps
	
ifneq ($(wildcard $(DEPS)), )
include $(DEPS)
endif

%.o : %.cpp makefile
	emcc $(CXXFLAGS) $< -o $@
