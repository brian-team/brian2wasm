PROGRAM = wasm_module.js

{% if emsdk_path %}{# Otherwise we assume it has been already activated globally #}
IGNORE := $(shell bash -c "{{emsdk_path}}/emsdk activate {{emsdk_version}} && source {{emsdk_path}}/emsdk_env.sh; env | sed 's/=/:=/' | sed 's/^/export /' > makeenv")
include makeenv
{% endif %}

SRCS = {{source_files}}
H_SRCS = {{header_files}}
OBJS = ${SRCS:.cpp=.o}
OPTIMISATIONS = {{ compiler_flags }} -O3 -ffast-math -fno-finite-math-only -std=c++11
CXXFLAGS = -c -Wno-write-strings $(OPTIMISATIONS) -I. {{ openmp_pragma('compilation') }} {{ compiler_debug_flags }} -fwasm-exceptions 
LFLAGS = {{ openmp_pragma('compilation') }} $(OPTIMISATIONS) {{ linker_flags }} {{ linker_debug_flags }} -fwasm-exceptions -sALLOW_MEMORY_GROWTH
all: $(PROGRAM)

.PHONY: all clean

$(PROGRAM): $(OBJS) $(DEPS) makefile {{ preamble_file }}
	emcc $(OBJS) -o $(PROGRAM) $(LFLAGS) {{ preloads }} --pre-js {{ preamble_file }} -sVERBOSE=1 -sMODULARIZE=1 -sENVIRONMENT=worker -sEXPORTED_FUNCTIONS=_main -sEXPORTED_RUNTIME_METHODS=callMain -sINVOKE_RUN=0

clean:
	{{ rm_cmd }}

make.deps: $(SRCS) $(H_SRCS)
	emcc $(CXXFLAGS) -MM $(SRCS) > make.deps
	
ifneq ($(wildcard $(DEPS)), )
include $(DEPS)
endif

%.o : %.cpp makefile
	emcc $(CXXFLAGS) $< -o $@
