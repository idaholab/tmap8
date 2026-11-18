/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once
#include <cmath>
#include "PhysicalConstants.h"
namespace PhysicalConstants
{
// Tritium half-life (seconds)
// https://nvlpubs.nist.gov/nistpubs/jres/105/4/j54luc2.pdf
const auto tritium_half_life = 388800000.0;
const auto tritium_decay_const = std::log(2.0) / tritium_half_life;
// Definition of a curie
// https://gnssn.iaea.org/main/bptc/BPTC%20Module%20Documents/Module01%20Nuclear%20physics%20and%20reactor%20theory.pdf}
const auto curie_to_bq = 3.7e10;
// Conversion coefficient from standard atmospheres to pascals (exact, by definition)
// https://physics.nist.gov/cgi-bin/cuu/Value?stdatm
const auto atm_to_Pa = 101325.0;
} // namespace PhysicalConstants
