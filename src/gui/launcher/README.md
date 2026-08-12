# Inicializador do WWA

### Conversão do ícone

https://www.icoconverter.com/

![logo](../resource/images/logo.ico)

### Compilação

Execute os comandos no **x64 Native Tools Command Prompt for VS 2022**:

```cmd
rc wwa.rc

cl wwa.c wwa.res /Fe:WWA.exe /link /SUBSYSTEM:WINDOWS /MANIFEST:EMBED /MANIFESTUAC:"level='requireAdministrator' uiAccess='false'"
```


