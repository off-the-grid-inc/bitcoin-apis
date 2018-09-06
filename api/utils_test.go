package poly

import (
	"testing"
	"fmt"

	"github.com/stretchr/testify/require"
	"github.com/betawaffle/gf256"
)


func TestTrue(t *testing.T) {
	require := require.New(t)

	x :=gf256.Element(240)
	y :=gf256.Element(60)
	z := gf256.Add(x,y)
	fmt.Println(z)
	require.Equal(z, gf256.Element(204), "not as expected")

}