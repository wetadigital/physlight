#TODO# usd_library(physAreaLight
#TODO# 
#TODO#     PUBLIC_HEADERS_INSTALL_PREFIX
#TODO#         ${ORGANIZATION}
#TODO# 
#TODO#     PYTHON_INSTALL_PREFIX
#TODO#         ${ORGANIZATION}
#TODO# 
#TODO#     LIBRARIES
#TODO#         js
#TODO#         plug
#TODO#         tf
#TODO#         sdf
#TODO#         vt
#TODO#         gf
#TODO#         usd
#TODO#         usdGeom
#TODO#         arch
#TODO# 
#TODO#     PUBLIC_CLASSES
#TODO#         triangle
#TODO# 
#TODO#     PUBLIC_HEADERS
#TODO#         api.h
#TODO#         tokens.h
#TODO# 
#TODO#     CPPFILES
#TODO#         tokens.cpp
#TODO# 
#TODO#     PYTHON_CPPFILES
#TODO#         moduleDeps.cpp
#TODO# 
#TODO#     PYMODULE_CPPFILES
#TODO#         module.cpp
#TODO#         wrapTokens.cpp
#TODO#         wrapTriangle.cpp
#TODO# 
#TODO#     PYTHON_FILES
#TODO#         __init__.py
#TODO# 
#TODO#     RESOURCE_FILES
#TODO#         generatedSchema.usda
#TODO#         plugInfo.json
#TODO# )
#TODO# 
#TODO# usd_executable(triangleCounter
#TODO# 
#TODO#     CPPFILES
#TODO#         triangleCounter.cpp
#TODO# 
#TODO#     LIBRARIES
#TODO#         tf
#TODO#         sdf
#TODO#         usd
#TODO#         usdTri
#TODO# )
#TODO# 
#TODO# add_subdirectory(tests)
#TODO# 
