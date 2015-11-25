_solvent()
{
  _script_commands="submitbuild submitproduct approve bring bringlabel localize addrequirement removerequirement fulfillrequirements checkrequirements printobjectstores printlabel"


  local cur prev
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "${_script_commands}" -- ${cur}) )

  return 0
}
complete -o nospace -F _solvent solvent
