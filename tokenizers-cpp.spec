%global __brp_add_determinism true
%define debug_package %{nil}

Name:           tokenizers-cpp
Version:        0.1.0
Release:        2%{?dist}
Summary:        C++ bindings for Hugging Face and SentencePiece tokenizers
License:        Apache-2.0
URL:            https://github.com/JeffKarling/tokenizers-cpp

# Source contains recursively cloned submodules
Source0:        tokenizers-cpp-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cargo
BuildRequires:  rust

%description
C++ bindings for Hugging Face and SentencePiece tokenizers, allowing local
tokenization in C++ applications.

%prep
%setup -q
sed -i '/fmacro-prefix-map/c\  add_compile_options("-fmacro-prefix-map=${CMAKE_SOURCE_DIR}/=")' sentencepiece/CMakeLists.txt




%build
export RUSTFLAGS="$RUSTFLAGS -C target-cpu=x86-64-v3"
%cmake -DCMAKE_BUILD_TYPE=Release \
       -DCMAKE_CXX_STANDARD=17 \
       -DCMAKE_CXX_STANDARD_REQUIRED=ON \
       -DCMAKE_CXX_FLAGS="-std=c++17 -march=x86-64-v3" \
       -DCMAKE_C_FLAGS="-march=x86-64-v3"
%cmake_build



%install
%cmake_install
if [ "%{_libdir}" != "%{_prefix}/lib" ]; then
    mkdir -p "%{buildroot}%{_libdir}/pkgconfig"
    mv "%{buildroot}%{_prefix}/lib"/lib*.a "%{buildroot}%{_libdir}/" || true
    mv "%{buildroot}%{_prefix}/lib"/pkgconfig/*.pc "%{buildroot}%{_libdir}/pkgconfig/" || true
    sed -i "s|libdir=\${prefix}/lib|libdir=%{_libdir}|g" "%{buildroot}%{_libdir}/pkgconfig/tokenizers_cpp.pc"
fi
rm -f "%{buildroot}%{_includedir}/msgpack.hpp"
rm -rf "%{buildroot}%{_includedir}/msgpack"
rm -rf "%{buildroot}%{_prefix}/lib/cmake"
rm -rf "%{buildroot}%{_prefix}/lib/pkgconfig"
rmdir "%{buildroot}%{_prefix}/lib" || true

# Install bundled abseil static libs (LTS 2026-01-07) that libsentencepiece.a
# depends on. The system abseil-cpp uses LTS 2024-07-22 with a different
# C++ inline namespace, so it cannot resolve these symbols at link time.
# Install to a private directory so they don't conflict with system abseil.
ABSL_DEST="%{buildroot}%{_libdir}/tokenizers-cpp-absl"
mkdir -p "${ABSL_DEST}"
find "%{_builddir}" -name "libabsl_*.a" -path "*/abseil-cpp/*" \
    -exec cp -n {} "${ABSL_DEST}/" \;

%files
%{_libdir}/libtokenizers_cpp.a
%{_libdir}/libtokenizers_c.a
%{_libdir}/libsentencepiece.a
%{_includedir}/tokenizers_cpp.h
%{_libdir}/pkgconfig/tokenizers_cpp.pc
%{_libdir}/tokenizers-cpp-absl/


%changelog
* Fri Jun 19 2026 Developer <developer@example.com> - 0.1.0-2
- Install bundled abseil LTS 2026-01-07 static libs to /usr/lib64/tokenizers-cpp-absl/
  so consumers can link libsentencepiece.a without system abseil namespace conflicts
* Sat Jun 13 2026 Developer <developer@example.com> - 0.1.0-1
- Initial RPM release
