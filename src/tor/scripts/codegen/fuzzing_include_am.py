#!/usr/bin/python

FUZZERS = """
	consensus
	descriptor
	diff
	diff-apply
	extrainfo
	hsdescv2
	hsdescv3
	http
	http-connect
	iptsv2
	microdesc
	vrs
"""


PREAMBLE = r"""
FUZZING_CPPFLAGS = \
	$(src_test_AM_CPPFLAGS) $(TEST_CPPFLAGS)
FUZZING_CFLAGS = \
	$(AM_CFLAGS) $(TEST_CFLAGS)
FUZZING_LDFLAG = \
	@TOR_LDFLAGS_zlib@ @TOR_LDFLAGS_openssl@ @TOR_LDFLAGS_libevent@
FUZZING_LIBS = \
	src/or/libtor-testing.a \
	src/common/libor-crypto-testing.a \
	$(LIBKECCAK_TINY) \
	$(LIBDONNA) \
	src/common/libor-testing.a \
	src/common/libor-ctime-testing.a \
	src/common/libor-event-testing.a \
	src/trunnel/libor-trunnel-testing.a \
	$(rust_ldadd) \
	@TOR_ZLIB_LIBS@ @TOR_LIB_MATH@ \
	@TOR_LIBEVENT_LIBS@ \
	@TOR_OPENSSL_LIBS@ @TOR_LIB_WS32@ @TOR_LIB_GDI@ @TOR_LIB_USERENV@ \
	@CURVE25519_LIBS@ \
	@TOR_SYSTEMD_LIBS@ \
	@TOR_LZMA_LIBS@ \
	@TOR_ZSTD_LIBS@

oss-fuzz-prereqs: \
	src/or/libtor-testing.a \
	src/common/libor-crypto-testing.a \
	$(LIBKECCAK_TINY) \
	$(LIBDONNA) \
	src/common/libor-testing.a \
	src/common/libor-ctime-testing.a \
	src/common/libor-event-testing.a \
	src/trunnel/libor-trunnel-testing.a

noinst_HEADERS += \
	src/test/fuzz/fuzzing.h

LIBFUZZER = -lFuzzer
LIBFUZZER_CPPFLAGS = $(FUZZING_CPPFLAGS) -DLLVM_FUZZ
LIBFUZZER_CFLAGS = $(FUZZING_CFLAGS)
LIBFUZZER_LDFLAG = $(FUZZING_LDFLAG)
LIBFUZZER_LIBS = $(FUZZING_LIBS) $(LIBFUZZER) -lstdc++

LIBOSS_FUZZ_CPPFLAGS = $(FUZZING_CPPFLAGS) -DLLVM_FUZZ
LIBOSS_FUZZ_CFLAGS = $(FUZZING_CFLAGS)
"""

POSTAMBLE = r"""
noinst_PROGRAMS += $(FUZZERS) $(LIBFUZZER_FUZZERS)
noinst_LIBRARIES += $(OSS_FUZZ_FUZZERS)
oss-fuzz-fuzzers:  oss-fuzz-prereqs $(OSS_FUZZ_FUZZERS)
fuzzers: $(FUZZERS) $(LIBFUZZER_FUZZERS)

test-fuzz-corpora: $(FUZZERS)
	$(top_srcdir)/src/test/fuzz_static_testcases.sh
"""

########### No user serviceable parts will follow.

PREAMBLE = PREAMBLE.strip()
POSTAMBLE = POSTAMBLE.strip()  # If I use it, it's a word!
FUZZERS = FUZZERS.split()
FUZZERS.sort()

WARNING = """
# This file was generated by fuzzing_include_am.py; do not hand-edit unless
# you enjoy having your changes erased.
""".strip()

print(WARNING)

print(PREAMBLE)

print("\n# ===== AFL fuzzers")

def get_id_name(s):
    return s.replace("-", "_")

for fuzzer in FUZZERS:
    idname = get_id_name(fuzzer)
    print("""\
if UNITTESTS_ENABLED
src_test_fuzz_fuzz_{name}_SOURCES = \\
	src/test/fuzz/fuzzing_common.c \\
	src/test/fuzz/fuzz_{name}.c
src_test_fuzz_fuzz_{name}_CPPFLAGS = $(FUZZING_CPPFLAGS)
src_test_fuzz_fuzz_{name}_CFLAGS = $(FUZZING_CFLAGS)
src_test_fuzz_fuzz_{name}_LDFLAGS = $(FUZZING_LDFLAG)
src_test_fuzz_fuzz_{name}_LDADD = $(FUZZING_LIBS)
endif
""".format(name=idname))

print("if UNITTESTS_ENABLED")
print("FUZZERS = \\")
print(" \\\n".join("\tsrc/test/fuzz/fuzz-{name}".format(name=fuzzer)
                   for fuzzer in FUZZERS))
print("endif")

print("\n# ===== libfuzzer")
print("\nif LIBFUZZER_ENABLED")

for fuzzer in FUZZERS:
    idname = get_id_name(fuzzer)
    print("""\
if UNITTESTS_ENABLED
src_test_fuzz_lf_fuzz_{name}_SOURCES = \\
	$(src_test_fuzz_fuzz_{name}_SOURCES)
src_test_fuzz_lf_fuzz_{name}_CPPFLAGS = $(LIBFUZZER_CPPFLAGS)
src_test_fuzz_lf_fuzz_{name}_CFLAGS = $(LIBFUZZER_CFLAGS)
src_test_fuzz_lf_fuzz_{name}_LDFLAGS = $(LIBFUZZER_LDFLAG)
src_test_fuzz_lf_fuzz_{name}_LDADD = $(LIBFUZZER_LIBS)
endif
""".format(name=idname))

print("LIBFUZZER_FUZZERS = \\")
print(" \\\n".join("\tsrc/test/fuzz/lf-fuzz-{name}".format(name=fuzzer)
                   for fuzzer in FUZZERS))

print("""
else
LIBFUZZER_FUZZERS =
endif""")

print("\n# ===== oss-fuzz\n")
print("if OSS_FUZZ_ENABLED")

for fuzzer in FUZZERS:
    idname = get_id_name(fuzzer)
    print("""\
if UNITTESTS_ENABLED
src_test_fuzz_liboss_fuzz_{name}_a_SOURCES = \\
	$(src_test_fuzz_fuzz_{name}_SOURCES)
src_test_fuzz_liboss_fuzz_{name}_a_CPPFLAGS = $(LIBOSS_FUZZ_CPPFLAGS)
src_test_fuzz_liboss_fuzz_{name}_a_CFLAGS = $(LIBOSS_FUZZ_CFLAGS)
endif
""".format(name=idname))

print("OSS_FUZZ_FUZZERS = \\")
print(" \\\n".join("\tsrc/test/fuzz/liboss-fuzz-{name}.a".format(name=fuzzer)
                   for fuzzer in FUZZERS))

print("""
else
OSS_FUZZ_FUZZERS =
endif""")

print("")

print(POSTAMBLE)
