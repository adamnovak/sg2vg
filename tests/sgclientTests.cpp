/*
 * Copyright (C) 2015 by Glenn Hickey (hickey@soe.ucsc.edu)
 *
 * Released under the MIT license, see LICENSE.txt
 */
#include <cstdio>
#include <cstdlib>
#include <sstream>
#include <ctime>
#include <cmath>
#include <cstdio>
#include <sstream>
#include "unitTests.h"
#include "sgclient.h"

using namespace std;


///////////////////////////////////////////////////////////
//  
//  
///////////////////////////////////////////////////////////
void dummyTest(CuTest *testCase)
{
  CuAssertTrue(testCase, true);
}

CuSuite* sgClientTestSuite(void) 
{
  CuSuite* suite = CuSuiteNew();
  SUITE_ADD_TEST(suite, dummyTest);
  return suite;
}
