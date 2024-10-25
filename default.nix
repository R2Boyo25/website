{ nixpkgs ? import <nixpkgs> {  } }:
 
let
  pkgs = with nixpkgs; [
    python312
    lessc
    poetry
  ];
 
in
  nixpkgs.stdenv.mkDerivation {
    name = "website";
    buildInputs = pkgs;
  }
