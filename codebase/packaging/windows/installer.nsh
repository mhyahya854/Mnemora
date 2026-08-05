!macro customHeader
  ManifestDPIAware true
!macroend

!macro customInstall
!macroend

!macro customUnInstall
  ${ifNot} ${isUpdated}
    StrCpy $0 "$PROFILE\.cache\mnemora\models"
    IfFileExists "$0\*.*" 0 +3
      RMDir /r "$0"
      DetailPrint "Removed Mnemora cached models"
    StrCpy $1 "$PROFILE\.cache\mnemora"
    RMDir "$1"
  ${endIf}
!macroend
