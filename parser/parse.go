package parser

import (
	"github.com/TobiEiss/go-textfsm/pkg/ast"
	"github.com/TobiEiss/go-textfsm/pkg/process"
	"github.com/TobiEiss/go-textfsm/pkg/reader"
)

func Parse(template string, input string, out chan<- []interface{}) error {
	// read template
	tmplCh := make(chan string)
	go reader.ReadLineByLine(template, tmplCh)

	srcCh := make(chan string)
	go reader.ReadLineByLine(input, srcCh)

	// create AST
	if ast, err := ast.CreateAST(tmplCh); err != nil {
		return err
	} else {
		// process ast
		if proc, err := process.NewProcess(ast, out); err != nil {
			return err
		} else {
			go proc.Do(srcCh)
		}
	}

	return nil
}
