package com.example.prawnvest

import java.time.LocalDate
import java.time.Period

//class Gotfromapi(var )

class Cndtn(var id: Int, var tm: String){

}
class Stock(var name: String, var oldprice: Float, var price: Float, var purchased:  String) {
}

class Strategy(var name: String, var lenghth: Int, var begin: String, var end: String, var conditions: List<Cndtn>,
               var stocks: List<Stock> = listOf())
{
    //var allstocks =
    fun go()
    {
        for (i in 0..lenghth)
        {
            //for (j in allstocks)
            {
                for (k in conditions)
                {

                }
            }
        }
    }
}

