package com.example.prawnvest

import java.time.LocalDate
import java.time.Period

//class Gotfromapi(var )

class Cndtn(var frtm: Int,var sctm: Int,var frper: Float,var scper: Float,var frb: Boolean,var scb: Boolean, var act: Boolean){

}
class Stock(var name: String, var oldprice: Int, var price: Int, var purchased:  String, var live: Int) {
}

class Strategy(var name: String, var lenghth: Int, var begin: String, var end: String, var conditions: List<Cndtn>,
               var stocks: List<Stock> = listOf(), var balance: Int)
{
    private var allstocks:List<Stock> = listOf()
    fun go()
    {
        for (i in 0..lenghth)
        {
            for (j in allstocks)
            {
                for (k in conditions)
                {
                    if(k.frtm > j.live) {
                        if(k.frb){
                            if(j.price / j.oldprice > k.frper){
                                if(k.act){
                                    buy(j, stocks)
                                }
                                else
                                {
                                    sell(j, stocks)
                                }
                            }
                        }
                        else{
                            if(j.price / j.oldprice < k.frper){
                                if(k.act){
                                    buy(j, stocks)
                                }
                                else
                                {
                                    sell(j, stocks)
                                }
                            }
                        }
                    }
                    else if(k.frtm + k.sctm > j.live) {
                        if(k.frb){
                            if(j.price / j.oldprice > k.scper){
                                if(k.act){
                                    buy(j, stocks)
                                }
                                else
                                {
                                    sell(j, stocks)
                                }
                            }
                        }
                        else{
                            if(j.price / j.oldprice < k.scper){
                                if(k.act){
                                    buy(j, stocks)
                                }
                                else
                                {
                                    sell(j, stocks)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    fun buy(q:Stock, stocks: List<Stock> = listOf())
    {
        this.stocks = stocks.plus(q)
        balance -= q.price

    }
    fun sell(q:Stock, stocks: List<Stock> = listOf()){
        this.stocks = stocks.minus(q)
        balance += q.price
    }
}

