with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell rec {
  buildInputs = [
    pythonPackages.python
    pythonPackages.pip

    pythonPackages.requests
    pythonPackages.pandas
    pythonPackages.beautifulsoup4
    pythonPackages.lxml

    pre-commit
  ];

  shellHook = ''
    [[ -d .venv ]] || python -m venv .venv
    source .venv/bin/activate
  '';

}
