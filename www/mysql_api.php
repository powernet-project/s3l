<?php 
  //parse_str($_GET, $querystring);
  //echo $querystring["table"];
  $sql_query = $_GET['query'];

  //--------------------------------------------------------------------------
  // Example php script for fetching data from mysql database
  //--------------------------------------------------------------------------
  $host = "localhost";
  $user = "root";
  $pass = "tiger257";

  $databaseName = "mytest";
  $tableName = "mytest";

  //--------------------------------------------------------------------------
  // 1) Connect to mysql database
  //--------------------------------------------------------------------------
  $con = mysql_connect($host,$user,$pass);
  $dbs = mysql_select_db($databaseName, $con);

  //--------------------------------------------------------------------------
  // 2) Query database for data
  //--------------------------------------------------------------------------
  $query = mysql_query($sql_query);          //query
  $json_output = array();
  while($result = mysql_fetch_assoc( $query )) {
    $json_output[] = $result;
  }
  //--------------------------------------------------------------------------
  // 3) echo result as json 
  //--------------------------------------------------------------------------
  echo json_encode($json_output);  
?>
