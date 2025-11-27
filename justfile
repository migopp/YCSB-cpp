default:
	just --list

build:
	cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build
	cp build/compile_commands.json .
	cmake --build build

clean:
	rm -rf build compile_commands.json
